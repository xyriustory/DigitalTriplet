from tkinter import messagebox
from SPARQLWrapper import SPARQLWrapper, JSON, TURTLE, BASIC
from pyfuseki import FusekiUpdate
from pyfuseki.utils import RdfUtils
from rdflib import Graph, RDFS, URIRef, Namespace, RDF, Literal
import datetime
import networkx as nx
import NXConverter
import setting

import importlib
importlib.reload(NXConverter)
importlib.reload(setting)

""" Fuseki操作クラス

"""

class FusekiManagement:
    def __init__(self, fuseki_url: str, dataset: str):
        """ 初期化

        """
        self.fuseki_url = fuseki_url
        self.dataset = dataset
        self.query_endpoint_url = '/'.join((fuseki_url, dataset, 'sparql'))
        self.update_endpoint_url = '/'.join((fuseki_url, dataset, 'update'))
        
    def get_fuseki_data_json(self, query):
        """ fusekiからデータを取得

        Args:
            query: 取得クエリ

        Returns:
            results: 取得json型の結果

        """
        sparql = SPARQLWrapper(self.query_endpoint_url)
        sparql.setQuery(query)
        sparql.setHTTPAuth(BASIC)
        sparql.setCredentials(setting.FUSEKI_ID, setting.FUSEKI_PW)

        sparql.setReturnFormat(JSON)
        results = sparql.query().convert()

        return results["results"]["bindings"]


    def get_graph(self, fuseki_url):
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
                    ?s ?p ?o.
                    }
            }
        """
        graph_list = []
        graph_url_list = []

        results = self.get_fuseki_data_json(query)
        if(len(results) > 0):
            for result in results:
                graph_url = result["graph"]["value"]
                graph_name = graph_url.replace(fuseki_url, "")
                graph_url_list.append(graph_url)
                graph_list.append(graph_name)
        else:
            messagebox.showerror("Error", "Fusekiにデータがありません!")

        return graph_url_list, graph_list


    def get_ttlfile_data(self, query, file_path):
        """ ttlファイルを取得

        Args:
            query: 取得するクエリ
            file_path: 保存フィアルパス

        """
        sparql = SPARQLWrapper(self.query_endpoint_url)
        sparql.setQuery(query)
        sparql.setHTTPAuth(BASIC)
        sparql.setCredentials(setting.FUSEKI_ID, setting.FUSEKI_PW)
        results = sparql.queryAndConvert()

        with open(file_path, "w", encoding="utf-8") as f:
            # bytes型をdecodeでstr型に変換する
            f.write(results.serialize())


    def get_graph_ttlfile(self, graph, ttl_file):
        """ 選択したグラフのttlファイルを取得

        Args:
            graph: 指定グラフ
            ttl_file: 保存フィアルパス

        """
        query_ttl_file = """
            CONSTRUCT { ?s ?p ?o}
            WHERE {
                graph """ + graph + """ {
                ?s ?p ?o.
                }
            }
        """
        self.get_ttlfile_data(query_ttl_file, ttl_file)


    def update(self, query):
        """ fusekiにあるデータを更新 (削除、更新)

        Args:
            query: 更新クエリ

        Returns:
            更新結果成功（True） 失敗（False）

        """
        sparql = SPARQLWrapper(self.update_endpoint_url)

        sparql.setQuery(query)
        sparql.method = "POST"
        sparql.setHTTPAuth(BASIC)
        sparql.setCredentials(setting.FUSEKI_ID, setting.FUSEKI_PW)

        query_results = sparql.query()
        result = query_results.response.read().decode()

        # 削除成功
        if result.find("Success") > 0:
            return True
        # 削除失敗
        return False


    def insert(self, graph_name, insert_data):
        """ Fusekiにデータを追加

        Args:
            graph_name: グラフ名
            insert_data: インサートデータ内容

        Returns:
            インサート成功（True）か失敗（False）

        """
        sparql = SPARQLWrapper(self.update_endpoint_url)

        sparql.method = "POST"
        sparql.setHTTPAuth(BASIC)
        sparql.setCredentials(setting.FUSEKI_ID, setting.FUSEKI_PW)

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
        sparql.setQuery(fuseki_query)

        query_results = sparql.query()

        result = query_results.response.read().decode()

        if result.find("Success") > 0:
            return True

        return False


    def ttlfile_export(self, win):
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

            self.get_graph_ttlfile(win.selected_graph_name, ttl_file_path)

            # graphmlファイルをエクスポート
            g_nx = nx.DiGraph()
            NXConverter.ttl_to_networkx(g_nx, ttl_file_path)
            nx.write_graphml(g_nx, graphml_file_path)

            messagebox.showinfo("確認", "エクスポートしました！", parent=win)


    def ttlfile_export_all(self, win):
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
                    ?subject ?predicate ?object.
                    }
            }
        """
        self.get_ttlfile_data(query, ttl_file_path)

        # graphmlファイルをエクスポート
        g_nx = nx.DiGraph()
        NXConverter.ttl_to_networkx(g_nx, ttl_file_path)
        nx.write_graphml(g_nx, graphml_file_path)

        messagebox.showinfo("確認", "エクスポートしました！", parent=win)

