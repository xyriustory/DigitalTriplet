from tkinter import messagebox
from SPARQLWrapper import SPARQLWrapper, JSON, TURTLE
from pyfuseki import FusekiUpdate
from pyfuseki.utils import RdfUtils
from rdflib import Graph, RDFS, URIRef, Namespace, RDF, Literal
import datetime
import networkx as nx
import NXConverter

import importlib
importlib.reload(NXConverter)


def get_fuseki_data_json(query):
    """ fusekiからデータを取得

    Args:
        query: 取得クエリ

    Returns:
        results: 取得json型の結果

    """
    sparql = SPARQLWrapper("http://localhost:3030/akiyama/sparql")
    sparql.setQuery(query)

    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()

    return results["results"]["bindings"]

def get_graph(fuseki_url):
    """ Fusekiからgraphとuriを取得

    Args:
        fuseki_url: fusekiのurl

    Returns:
        graph_url_list: 取得したuriリスト
        graph_list: 取得したグラフ名リスト

    """
    query = """
        PREFIX pd3: <http://DigitalTriplet.net/2021/08/ontology#>
        select distinct ?graph
        where {
                graph ?graph {
                ?s ?p ?o;
                }
        }
    """
    graph_list = []
    graph_url_list = []

    results = get_fuseki_data_json(query)
    if(len(results) > 0):
        for result in results:
            graph_url = result["graph"]["value"]
            graph_name = graph_url.replace(fuseki_url, "")
            graph_url_list.append(graph_url)
            graph_list.append(graph_name)
    else:
        messagebox.showerror("Error", "Fusekiにデータがありません!")

    return graph_url_list, graph_list

def get_ttlfile_data(query, file_path):
    """ ttlファイルを取得

    Args:
        query: 取得するクエリ
        file_path: 保存フィアルパス

    """
    sparql = SPARQLWrapper("http://localhost:3030/akiyama/sparql")
    sparql.setQuery(query)

    sparql.setReturnFormat(TURTLE)
    results = sparql.query().convert()

    with open(file_path, "w", encoding="utf-8") as f:
        # bytes型をdecodeでstr型に変換する
        f.write(results.decode())

def get_graph_ttlfile(graph, ttl_file):
    """ 選択したグラフのttlファイルを取得

    Args:
        graph: 指定グラフ
        ttl_file: 保存フィアルパス

    """
    query_ttl_file = """
        CONSTRUCT { ?s ?p ?o}
        WHERE {
            graph """ + graph + """ {
            ?s ?p ?o;
            }
        }
    """
    get_ttlfile_data(query_ttl_file, ttl_file)

def fuseki_update(query):
    """ fusekiにあるデータを更新 (削除、更新)

    Args:
        query: 更新クエリ

    Returns:
        更新結果成功（True） 失敗（False）

    """
    sparql = SPARQLWrapper("http://localhost:3030/akiyama/update")

    sparql.setQuery(query)
    sparql.method = "POST"
    sparql.query()

    query_results = sparql.query()
    result = query_results.response.read().decode()

    # 削除成功
    if result.find("Success") > 0:
        return True
    # 削除失敗
    return False

def fuseki_insert(graph_name, insert_data):
    """ Fusekiにデータを追加

    Args:
        graph_name: グラフ名
        insert_data: インサートデータ内容

    Returns:
        インサート成功（True）か失敗（False）

    """
    fuseki = FusekiUpdate("http://localhost:3030", "akiyama")
    g = Graph()

    RdfUtils.add_list_to_graph(g, insert_data)
    spo_str = "\n".join(
        [f"{s.n3()} {p.n3()} {o.n3()}." for (s, p, o) in g]
    )

    fuseki_query = """
                PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
                INSERT DATA {
                    GRAPH """ + graph_name + "{" + spo_str + """} 
                }
                """
    query_results = fuseki.run_sparql(fuseki_query)

    result = query_results.response.read().decode()

    if result.find("Success") > 0:
        return True

    return False

def fuseki_export(win):
    """ Fusekiから単一グラフデータをエクスポート

    Args:
        win: 実行するウィンドウ

    """
    if (win.selected_graph_name is None):
        messagebox.showerror("Error", "No graph selected!", parent=win)
    else:
        now = datetime.datetime.now()
        # ttlファイルをエクスポート
        ttl_file_path = "fuseki_browser_export_" + \
            now.strftime("%Y%m%d_%H%M%S") + ".ttl"
        graphml_file_path = "fuseki_browser_export_" + \
            now.strftime("%Y%m%d_%H%M%S") + ".graphml"

        get_graph_ttlfile(win.selected_graph_name, ttl_file_path)

        # graphmlファイルをエクスポート
        g_nx = nx.DiGraph()
        NXConverter.ttl_to_networkx(g_nx, ttl_file_path)
        nx.write_graphml(g_nx, graphml_file_path)

        messagebox.showinfo("確認", "エクスポートしました！", parent=win)

def fuseki_export_all(win):
    """ Fusekiから全データをエクスポート

    Args:
        win: 実行するウィンドウ

    """
    now = datetime.datetime.now()
    # ttlファイルをエクスポート
    ttl_file_path = "fuseki_browser_export_all_" + \
        now.strftime("%Y%m%d_%H%M%S") + ".ttl"
    graphml_file_path = "fuseki_browser_export_all_" + \
        now.strftime("%Y%m%d_%H%M%S") + ".graphml"
    query = """
        CONSTRUCT {?subject ?predicate ?object}
        WHERE {
                graph ?gen {
                ?subject ?predicate ?object
                }
        }
    """
    get_ttlfile_data(query, ttl_file_path)

    # graphmlファイルをエクスポート
    g_nx = nx.DiGraph()
    NXConverter.ttl_to_networkx(g_nx, ttl_file_path)
    nx.write_graphml(g_nx, graphml_file_path)

    messagebox.showinfo("確認", "エクスポートしました！", parent=win)
