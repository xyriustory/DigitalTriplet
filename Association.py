
from tkinter import messagebox

import random
import string
import datetime
from rdflib import Graph, RDFS, URIRef, Namespace, RDF, Literal

import FusekiManagement as fm
import DataManagement as data_mg
import setting

import importlib
importlib.reload(fm)
importlib.reload(data_mg)
importlib.reload(setting)

""" 関連付け処理クラス

"""


def insert_member_new(graph_name, current_item, node_id, member_graph, \
                    member_uri, new_uri, parent):
    """ member関連付け処理で追加するデータを用意

    Args:
        graph_name: グラフ名
        current_item: ノードバリュー
        node_id: ノードid
        member_graph: メンバーグラフ名
        member_uri: メンバーuri
        new_uri: コピーした新uri
        parent: 実行するウィンドウ

    """
    fuseki = fm.FusekiManagement(setting.FUSEKI_URL, setting.FUSEKI_DB)
    fuseki_insert_data_mem = []
    fuseki_insert_data = []
    member_node_list = []
    object_list = []
    layer = None
    pd3 = Namespace("http://DigitalTriplet.net/2021/08/ontology#")

    # --------------------------------------------------------------
    # memberとmemberのlayerを取得
    # --------------------------------------------------------------
    member_query = """
        PREFIX pd3: <http://DigitalTriplet.net/2021/08/ontology#>
        SELECT distinct ?node ?layer
        WHERE {
            graph """ + member_graph + """ {
            ?node ?p pd3:Action;
                    pd3:layer ?layer.
            filter(regex(str(?node),""" + '"' + member_uri + '"' + """)) 
            FILTER NOT EXISTS {?node pd3:attribution ?parent}
            }
        }
    """
    query_result = fuseki.get_fuseki_data_json(member_query)
    for result in query_result:
        node = result["node"]["value"].replace(member_uri, new_uri)
        member_node_list.append(node)
        layer = result["layer"]["value"]

    # --------------------------------------------------------------
    # objectを取得
    # --------------------------------------------------------------
    member_query = """
        PREFIX pd3: <http://DigitalTriplet.net/2021/08/ontology#>
        SELECT distinct ?node ?layer
        WHERE {
            graph """ + member_graph + """ {
            ?node ?p pd3:Object;
                    pd3:layer ?layer.
            filter(regex(str(?node),""" + '"' + member_uri + '"' + """)) 
            FILTER NOT EXISTS {?node pd3:attribution ?parent}
            }
        }
    """
    query_result = fuseki.get_fuseki_data_json(member_query)
    for result in query_result:
        object_node = result["node"]["value"].replace(member_uri, new_uri)
        object_list.append(object_node)
    # --------------------------------------------------------------
    # containerを追加
    # --------------------------------------------------------------
    # container名
    container_name = "".join(random.choice(
        string.ascii_letters + string.digits) for _ in range(22))

    # RDF.type
    fuseki_insert_data_mem.append([URIRef(new_uri)+URIRef(container_name), \
                                RDF.type, pd3.Container])
    # containerType
    fuseki_insert_data_mem.append([URIRef(new_uri)+URIRef(container_name), \
                                pd3.containerType, Literal("specialization")])
    # contraction
    fuseki_insert_data_mem.append([URIRef(new_uri)+URIRef(container_name), \
                                pd3.contraction, URIRef(new_uri)+URIRef(node_id)])
    # id
    fuseki_insert_data_mem.append([URIRef(new_uri)+URIRef(container_name), \
                                pd3.id, Literal(container_name)])
    # geoBoundingHeight
    fuseki_insert_data_mem.append([URIRef(new_uri)+URIRef(container_name), \
                                pd3.geoBoundingHeight, Literal("200")])
    # geoBoundingWidth
    fuseki_insert_data_mem.append([URIRef(new_uri)+URIRef(container_name), \
                                pd3.geoBoundingWidth, Literal("400")])
    # layer
    fuseki_insert_data_mem.append([URIRef(new_uri)+URIRef(container_name), \
                                pd3.layer, Literal(layer)])
    # member
    for member in member_node_list:
        fuseki_insert_data_mem.append([URIRef(new_uri)+URIRef(container_name), \
                                    pd3.member, URIRef(member)])
    # output
    fuseki_insert_data_mem.append([URIRef(new_uri)+URIRef(container_name), \
                                pd3.output, URIRef(new_uri)+URIRef(node_id)])
    # value
    fuseki_insert_data_mem.append([URIRef(new_uri)+URIRef(container_name), \
                                pd3.value, Literal(current_item)])
    # --------------------------------------------------------------
    # actionのexpansionを追加
    # --------------------------------------------------------------
    fuseki_insert_data.append([URIRef(new_uri)+URIRef(node_id), \
                            pd3.expansion, URIRef(new_uri)+URIRef(container_name)])
    # --------------------------------------------------------------
    # memberのattributionを追加
    # --------------------------------------------------------------
    for member in member_node_list:
        fuseki_insert_data_mem.append([URIRef(member), pd3.attribution, \
                                    URIRef(new_uri)+URIRef(container_name)])
    # --------------------------------------------------------------
    # objectのattributionを追加
    # --------------------------------------------------------------
    for object in object_list:
        fuseki_insert_data_mem.append([URIRef(object), pd3.attribution, \
                                    URIRef(new_uri)+URIRef(container_name)])
    # --------------------------------------------------------------
    # container flowを追加
    # --------------------------------------------------------------
    container_flow_name = "".join(random.choice(
        string.ascii_letters + string.digits) for _ in range(22))
    # RDF.type
    fuseki_insert_data_mem.append([URIRef(new_uri)+URIRef(container_flow_name), \
                                RDF.type, pd3.ContainerFlow])
    # arcType
    fuseki_insert_data_mem.append([URIRef(new_uri)+URIRef(container_flow_name), \
                                pd3.arcType, Literal("hierarchization")])
    # id
    fuseki_insert_data_mem.append([URIRef(new_uri)+URIRef(container_flow_name), \
                                pd3.id, Literal(container_flow_name)])
    # layer
    fuseki_insert_data_mem.append([URIRef(new_uri)+URIRef(container_flow_name), \
                                pd3.layer, Literal(layer)])
    # source
    fuseki_insert_data_mem.append([URIRef(new_uri)+URIRef(container_flow_name), \
                                pd3.source, URIRef(new_uri)+URIRef(container_name)])
    # target
    fuseki_insert_data_mem.append([URIRef(new_uri)+URIRef(container_flow_name), \
                                pd3.target, URIRef(new_uri)+URIRef(node_id)])
    # value
    fuseki_insert_data_mem.append([URIRef(new_uri)+URIRef(container_flow_name), \
                                pd3.value, Literal("")])
    # --------------------------------------------------------------
    # actionのinputを追加
    # --------------------------------------------------------------
    fuseki_insert_data.append([URIRef(new_uri)+URIRef(node_id), \
                            pd3.input, URIRef(new_uri)+URIRef(container_flow_name)])

    if not fuseki.insert(graph_name, fuseki_insert_data):
        messagebox.showerror("Error", "インサート失敗!", parent=parent)
    else:
        if fuseki.insert(member_graph, fuseki_insert_data_mem):
            messagebox.showinfo("確認", "Fusekiにインサートしました！", parent=parent)
        else:
            messagebox.showerror("Error", "インサート失敗!", parent=parent)


def delete_member(graph_name, ori_uri, node_uri, node_name, node_id, node_list, \
                node_id_list, object_id_list, parent):
    """ member関連付け削除処理

    Args:
        graph_name: グラフ名
        ori_uri: GPM uri
        node_uri: ノードuri
        node_name: ノード名
        node_id: ノードid
        node_list: ノード名リスト
        node_id_list: ノードidリスト
        object_id_list: オブジェクトidリスト
        parent: 実行するウィンドウ

    """
    fuseki = fm.FusekiManagement(setting.FUSEKI_URL, setting.FUSEKI_DB)
    contraction = []
    member_id_list = node_id_list[node_id]
    # コンテナ情報を取得
    query = """
        PREFIX pd3: <http://DigitalTriplet.net/2021/08/ontology#>
        SELECT ?s ?id ?contraction
        WHERE {
                graph """ + graph_name + """ {
                ?s ?p pd3:Container;
                    pd3:contraction ?contraction;
                    pd3:id ?id;
                    pd3:value ?value.
            FILTER(?value = """ + '"' + node_name + '"' + """)
            FILTER(regex(str(?s),""" + '"' + node_uri + '"' + """)) 
            }
        }
    """
    query_result = fuseki.get_fuseki_data_json(query)
    if(len(query_result) > 0):
        for result in query_result:
            con_id = result["id"]["value"]
            con_subject = result["s"]["value"]
            contraction.append(result["contraction"]["value"])
            con_uri = con_subject.replace(con_id, "")

    # コンテナフロー情報を取得
    flow_query = """
        PREFIX pd3: <http://DigitalTriplet.net/2021/08/ontology#>
        SELECT ?s ?id
        WHERE {
                graph """ + graph_name + """ {
                ?s ?p pd3:ContainerFlow;
                    pd3:source ?source;
                    pd3:id ?id;
                    pd3:target ?target.
            FILTER(?source= """ + '<' + con_subject + '>' + """)
            FILTER(?target= """ + '<' + node_uri + node_id + '>' + """)
            FILTER(regex(str(?s),""" + '"' + node_uri + '"' + """)) 
            }
        }
    """
    flow_result = fuseki.get_fuseki_data_json(flow_query)
    if(len(flow_result) > 0):
        for result in flow_result:
            flow_subject = result["s"]["value"]
            flow_id = result["id"]["value"]

    # コンテナフロー削除クエリ
    flow_query = """
        PREFIX pd3: <http://DigitalTriplet.net/2021/08/ontology#>
        WITH """ + graph_name + """
        DELETE { ?s ?p ?o }
        WHERE { ?s ?p ?o ; 
                pd3:id """ + '"' + flow_id + '"' + """.
                FILTER(regex(str(?s),""" + '"' + node_uri + '"' + """))}
    """

    # 親のexpansion削除クエリ
    exp_query = """
        PREFIX pd3: <http://DigitalTriplet.net/2021/08/ontology#>
        WITH """ + graph_name + """
        DELETE { ?s pd3:expansion """ + "<" + con_subject + ">" + """ }
        WHERE { ?s ?p ?o ; 
                pd3:id """ + '"' + node_id + '"' + """. 
                FILTER(regex(str(?s),""" + '"' + node_uri + '"' + """))}
    """

    if fuseki.update(exp_query) and fuseki.update(flow_query):
        if(len(contraction) > 1):
            # コンテナが複数アクションと繋がっている場合
            # 繋がりのみを削除
            delete_con_data = "<" + node_uri + node_id + ">"
            query_del_contraction = """
                PREFIX pd3: <http://DigitalTriplet.net/2021/08/ontology#>
                WITH """ + graph_name + """
                DELETE { ?s pd3:contraction """ + delete_con_data + """ }
                WHERE { ?s ?p ?o ; 
                        pd3:id """ + '"' + con_id + '"' + """. 
                        FILTER(regex(str(?s),""" + '"' + node_uri + '"' + """))}
            """

            query_del_output = """
                PREFIX pd3: <http://DigitalTriplet.net/2021/08/ontology#>
                WITH """ + graph_name + """
                DELETE { ?s pd3:output """ + delete_con_data + """ }
                WHERE { ?s ?p ?o ; 
                        pd3:id """ + '"' + con_id + '"' + """. 
                        FILTER(regex(str(?s),""" + '"' + node_uri + '"' + """))}
            """
            if fuseki.update(query_del_contraction) and \
                fuseki.update(query_del_output):
                messagebox.showinfo("確認", "削除しました！")
            else:
                messagebox.showerror("Error", "削除失敗!")

        else:
            # 一つアクションと繋がっている場合
            # コンテナ削除クエリ
            con_query = """
                PREFIX pd3: <http://DigitalTriplet.net/2021/08/ontology#>
                WITH """ + graph_name + """
                DELETE { ?s ?p ?o }
                WHERE { ?s ?p ?o ; 
                        pd3:id """ + '"' + con_id + '"' + """. 
                        FILTER(regex(str(?s),""" + '"' + node_uri + '"' + """))}
            """
            item_list = member_id_list + object_id_list
            if fuseki.update(con_query):
                # コンテナのメンバーとオブジェクトのattribution削除クエリ
                for item_id in item_list:
                    attr_query = """
                        PREFIX pd3: <http://DigitalTriplet.net/2021/08/ontology#>
                        WITH """ + graph_name + """
                        DELETE { ?s pd3:attribution """ + "<" + con_subject + ">" + """ }
                        WHERE { ?s ?p ?o ; 
                                pd3:id """ + '"' + item_id + '"' + """. 
                                FILTER(regex(str(?s),""" + '"' + node_uri + '"' + """))}
                    """
                    if fuseki.update(attr_query):
                        continue
                    else:
                        messagebox.showerror("Error", "削除失敗!", parent=parent)

                # 親のuriとコンテナのuri一致する場合、uri入り替え処理

                if(node_uri == con_uri):
                    change_child_uri_new(graph_name, ori_uri, con_uri, \
                        node_id, node_list, node_id_list, parent)

                messagebox.showinfo("確認", "削除しました！", parent=parent)

    else:
        messagebox.showerror("Error", "削除失敗!", parent=parent)


def change_child_uri_new(graph_name, ori_uri, uri, node_id, uri_node_list, \
                        uri_node_id_list, parent):
    """ uri入り替え処理

    Args:
        graph_name: グラフ名
        ori_uri: GPM uri
        uri: ノードuri
        node_id: ノードid
        uri_node_list: ノード名リスト
        uri_node_id_list: ノードidリスト
        parent: 実行するウィンドウ

    """
    fuseki = fm.FusekiManagement(setting.FUSEKI_URL, setting.FUSEKI_DB)
    data = data_mg.DataManagement()
    container_count = data.get_ep_container_count(graph_name, uri)

    node_list = {}
    id_list = {}
    node_list["top"] = uri_node_list[node_id]
    id_list["top"] = uri_node_id_list[node_id]

    (node_list, id_list) = data.get_member(container_count, False, \
        uri_node_list, uri_node_id_list, node_list, id_list)

    # 新uriを生成
    now = datetime.datetime.now()
    new_uri = "http://localhost/Container_delete_" + \
        now.strftime("%Y%m%d_%H%M%S") + "_part2" + "/"

    update_data_list = data.get_node_rdf_info(graph_name, uri, id_list)

    # 更新したいノードを削除して、新たな値をインサートする
    fuseki_insert_data = []
    #print(update_data_list)
    # 削除
    for update_node_id in update_data_list.keys():
        delete_query = """
        PREFIX pd3: <http://DigitalTriplet.net/2021/08/ontology#>
        WITH """ + graph_name + """
        DELETE { """ + '<' + uri + update_node_id + '>' + """ ?property ?value } 
        WHERE { """ + '<' + uri + update_node_id + '>' + """ ?property ?value. } 
        """
        if(fuseki.update(delete_query)):
            continue
        else:
            messagebox.showerror("Error", "削除失敗!", parent=parent)

    # uriを入れ替えるため、新プロセスノードを追加
    object_ep = "http://DigitalTriplet.net/2021/08/ontology#EngineeringProcess"
    update_data_list[new_uri] = []
    update_data_list[new_uri].append(["http://www.w3.org/1999/02/22-rdf-syntax-ns#type", \
                                    object_ep])
    # drivesを追加    
    update_data_list[new_uri].append(["http://DigitalTriplet.net/2021/08/ontology#drives", \
                                    ori_uri])

    # インサート
    for update_node_id in update_data_list.keys():
        for rdf_info in update_data_list[update_node_id]:
            # objectを用意
            if(rdf_info[0] == "http://www.w3.org/1999/02/22-rdf-syntax-ns#type") or \
                (rdf_info[0] == "http://DigitalTriplet.net/2021/08/ontology#drives"):
                object = URIRef(rdf_info[1])
            elif(rdf_info[0] == "http://DigitalTriplet.net/2021/08/ontology#attribution") or \
                (rdf_info[0] == "http://DigitalTriplet.net/2021/08/ontology#expansion") or \
                (rdf_info[0] == "http://DigitalTriplet.net/2021/08/ontology#contraction") or \
                (rdf_info[0] == "http://DigitalTriplet.net/2021/08/ontology#output") or \
                (rdf_info[0] == "http://DigitalTriplet.net/2021/08/ontology#input") or \
                (rdf_info[0] == "http://DigitalTriplet.net/2021/08/ontology#member") or \
                (rdf_info[0] == "http://DigitalTriplet.net/2021/08/ontology#source") or \
                    (rdf_info[0] == "http://DigitalTriplet.net/2021/08/ontology#target"):
                object = URIRef(rdf_info[1].replace(uri, new_uri))
            else:
                object = Literal(rdf_info[1])
            # インサートデータを用意
            if(object == URIRef(object_ep)) or \
                (rdf_info[0] == "http://DigitalTriplet.net/2021/08/ontology#drives"):
                # プロセスノードはidがないため
                fuseki_insert_data.append([URIRef(new_uri), \
                                        URIRef(rdf_info[0]), object])
            else:
                fuseki_insert_data.append([URIRef(new_uri)+URIRef(update_node_id), \
                                        URIRef(rdf_info[0]), object])

    if fuseki.insert(graph_name, fuseki_insert_data) == False:
        messagebox.showerror('Error', '削除失敗!', parent=parent)


def change_child_uri(graph_name, uri, member_list, member_id_list, parent):
    """ uri入り替え処理

    Args:
        graph_name: グラフ名
        uri: 古uri
        member_list: メンバー名リスト
        member_id_list: メンバーidリスト
        parent: 実行するウィンドウ

    """
    fuseki = fm.FusekiManagement(setting.FUSEKI_URL, setting.FUSEKI_DB)
    data = data_mg.DataManagement()
    container_count = data.get_ep_container_count(graph_name, uri)

    node_list = {}
    id_list = {}
    node_list['top'] = member_list
    id_list['top'] = member_id_list

    if(container_count != 0):
        (node_list, id_list) = data.get_member_by_fuseki(graph_name, uri, \
                                        container_count, \
                                        False, node_list, id_list)

    # 新uriを生成
    new_uri = "http://" + \
        "".join(random.choice(string.ascii_letters + string.digits)
                for _ in range(10)) + "/"
    # 新prefix
    new_prefix = "new-" + \
        "".join(random.choice(string.ascii_letters + string.digits)
                for _ in range(10))

    update_data_list = data.get_node_rdf_info(graph_name, uri, id_list)

    # 更新したいノードを削除して、新たな値をインサートする
    fuseki_insert_data = []

    # 削除
    for update_node_id in update_data_list.keys():
        delete_query = """
        PREFIX pd3: <http://DigitalTriplet.net/2021/08/ontology#>
        WITH """ + graph_name + """
        DELETE { """ + '<' + uri + update_node_id + '>' + """ ?property ?value } 
        WHERE { """ + '<' + uri + update_node_id + '>' + """ ?property ?value. } 
        """
        if(fuseki.update(delete_query)):
            continue
        else:
            messagebox.showerror("Error", "削除失敗!", parent=parent)

    # インサート
    for update_node_id in update_data_list.keys():
        for rdf_info in update_data_list[update_node_id]:
            if(rdf_info[0] == "http://www.w3.org/1999/02/22-rdf-syntax-ns#type"):
                object = URIRef(rdf_info[1])
            elif(rdf_info[0] == "http://DigitalTriplet.net/2021/08/ontology#attribution") or \
                (rdf_info[0] == "http://DigitalTriplet.net/2021/08/ontology#expansion") or \
                (rdf_info[0] == "http://DigitalTriplet.net/2021/08/ontology#contraction") or \
                (rdf_info[0] == "http://DigitalTriplet.net/2021/08/ontology#output") or \
                (rdf_info[0] == "http://DigitalTriplet.net/2021/08/ontology#input") or \
                (rdf_info[0] == "http://DigitalTriplet.net/2021/08/ontology#member") or \
                (rdf_info[0] == "http://DigitalTriplet.net/2021/08/ontology#source") or \
                    (rdf_info[0] == "http://DigitalTriplet.net/2021/08/ontology#target"):
                object = URIRef(rdf_info[1].replace(uri, new_uri))
            else:
                object = Literal(rdf_info[1])

            fuseki_insert_data.append([URIRef(new_uri)+URIRef(update_node_id), \
                                    URIRef(rdf_info[0]), object])

    if fuseki.insert(graph_name, fuseki_insert_data) == False:
        messagebox.showerror('Error', '削除失敗!', parent=parent)


def change_object_uri(graph_name, uri, supflow_subject):
    """ オブジェクト uri入り替えdataを取得

    Args:
        graph_name: グラフ名
        uri: 古uri
        supflow_subject: メンバー名リスト

    Returns:
        update_data_list: uri更新するデータリスト

    """
    fuseki = fm.FusekiManagement(setting.FUSEKI_URL, setting.FUSEKI_DB)
    data = data_mg.DataManagement()
    update_data_list = {}
    # obecjt更新データを取得
    object_query = """
        PREFIX pd3: <http://DigitalTriplet.net/2021/08/ontology#>
            SELECT distinct ?id
            WHERE {
                graph """ + graph_name + """ {
                    ?s ?p pd3:Object;
                    pd3:id ?id;
                    pd3:output ?output.
                FILTER(?output = """ + supflow_subject + """)
                }
            }
    """
    object_result = fuseki.get_fuseki_data_json(object_query)
    if(len(object_result) > 0):
        for result in object_result:
            object_id = result["id"]["value"]

        # object詳細データを取得と更新
        object_subject = "<" + uri + object_id + ">"
        update_data_list[object_id] = []

        object_detail_query_result = data.get_update_detail_data(
            graph_name, object_subject)
        if(len(object_detail_query_result) > 0):
            for result in object_detail_query_result:
                predicate = result["p"]["value"]
                object = result["o"]["value"]
                update_data_list[object_id].append([predicate, object])

    return update_data_list


def insert_con_member_new(graph_name, current_item, node_id, uri, \
        container_id, parent):
    """ コンテナmember関連付け処理

    Args:
        graph_name: グラフ名
        current_item: ノード名
        node_id: ノードid
        uri: ノードuri
        container_id: 関連付けするコンテナid
        parent: 実行するウィンドウ

    """
    fuseki = fm.FusekiManagement(setting.FUSEKI_URL, setting.FUSEKI_DB)
    fuseki_insert_data = []
    fuseki_inset_data_con = []
    pd3 = Namespace("http://DigitalTriplet.net/2021/08/ontology#")

    container = uri + container_id

    # container value, layerを取得
    container_query = """
        PREFIX pd3: <http://DigitalTriplet.net/2021/08/ontology#>
        SELECT ?layer ?value
        WHERE {
            graph """ + graph_name + """ {
            ?s ?p pd3:Container;
            pd3:value ?value;
            pd3:layer ?layer.
            FILTER(?s = """ + '<' + container + '>' + """)
            }
        }
    """
    container_result = fuseki.get_fuseki_data_json(container_query)
    if(len(container_result) > 0):
        for con_result in container_result:
            layer = con_result["layer"]["value"]
            value = con_result["value"]["value"]

    # --------------------------------------------------------------
    # containerの親情報を更新
    # --------------------------------------------------------------
    # 削除
    query_del_contraction = """
        PREFIX pd3: <http://DigitalTriplet.net/2021/08/ontology#>
        WITH """ + graph_name + """
        DELETE { ?s pd3:contraction ?o }
        WHERE { ?s ?p ?o.
                FILTER(?s = """ + '<' + container + '>' + """)}
    """

    query_del_output = """
        PREFIX pd3: <http://DigitalTriplet.net/2021/08/ontology#>
        WITH """ + graph_name + """
        DELETE { ?s pd3:output ?o }
        WHERE { ?s ?p ?o.
                FILTER(?s = """ + '<' + container + '>' + """)}
    """

    # 追加
    # contraction
    fuseki_insert_data.append([URIRef(container), pd3.contraction, \
                                URIRef(uri)+URIRef(node_id)])

    # output
    fuseki_insert_data.append([URIRef(container), pd3.output, \
                                URIRef(uri)+URIRef(node_id)])

    # --------------------------------------------------------------
    # container flowを追加
    # --------------------------------------------------------------
    container_flow_name = "".join(random.choice(
        string.ascii_letters + string.digits) for _ in range(22))
    # RDF.type
    fuseki_insert_data.append([URIRef(uri)+URIRef(container_flow_name), \
                                RDF.type, pd3.ContainerFlow])
    # arcType
    fuseki_insert_data.append([URIRef(uri)+URIRef(container_flow_name), \
                                pd3.arcType, Literal("hierarchization")])
    # id
    fuseki_insert_data.append([URIRef(uri)+URIRef(container_flow_name), \
                                pd3.id, Literal(container_flow_name)])
    # layer
    fuseki_insert_data.append([URIRef(uri)+URIRef(container_flow_name), \
                                pd3.layer, Literal(layer)])
    # source
    fuseki_insert_data.append([URIRef(uri)+URIRef(container_flow_name), \
                                pd3.source, URIRef(container)])
    # target
    fuseki_insert_data.append([URIRef(uri)+URIRef(container_flow_name), \
                                pd3.target, URIRef(uri)+URIRef(node_id)])
    # value
    fuseki_insert_data.append([URIRef(uri)+URIRef(container_flow_name), \
                                pd3.value, Literal("")])

    # --------------------------------------------------------------
    # actionのexpansionを追加
    # --------------------------------------------------------------
    fuseki_insert_data.append([URIRef(uri)+URIRef(node_id), \
                            pd3.expansion, URIRef(container)])

    # --------------------------------------------------------------
    # actionのinputを追加
    # --------------------------------------------------------------
    fuseki_insert_data.append([URIRef(uri)+URIRef(node_id), \
                            pd3.input, URIRef(uri)+URIRef(container_flow_name)])

    if fuseki.update(query_del_contraction) and \
        fuseki.update(query_del_output):
        if fuseki.insert(graph_name, fuseki_insert_data):
            # actionのバリューを更新（コンテナ名と一致するため）
            update_query = """
                PREFIX pd3: <http://DigitalTriplet.net/2021/08/ontology#>
                WITH """ + graph_name + """
                DELETE { """ + "<" + uri+node_id + ">" + """ pd3:value """ + '"' + current_item + '"' + """ }
                INSERT { """ + "<" + uri+node_id + ">" + """ pd3:value """ + '"' + value + '"' + """ }
                WHERE {
                """ + "<" + uri+node_id + ">" + """ pd3:value """ + '"' + current_item + '"' + """.
                }
            """
            if fuseki.update(update_query):
                messagebox.showinfo("確認", "メンバー関連付け成功しました！", parent=parent)
        else:
            messagebox.showerror("Error", "メンバー関連付け失敗しました!", parent=parent)
    else:
        messagebox.showerror("Error", "メンバー関連付け失敗しました!", parent=parent)


def insert_con_member(graph_name, current_item, node_id, uri, \
        container, parent):
    """ コンテナmember関連付け処理

    Args:
        graph_name: グラフ名
        current_item: ノード名
        node_id: ノードid
        uri: ノードuri
        container_id: 関連付けするコンテナid
        parent: 実行するウィンドウ

    """
    fuseki = fm.FusekiManagement(setting.FUSEKI_URL, setting.FUSEKI_DB)
    fuseki_insert_data = []
    pd3 = Namespace("http://DigitalTriplet.net/2021/08/ontology#")

    # container uri, id, layerを取得
    container_query = """
        PREFIX pd3: <http://DigitalTriplet.net/2021/08/ontology#>
        SELECT ?id ?layer ?value
        WHERE {
            graph """ + graph_name + """ {
            ?s ?p pd3:Container;
            pd3:layer ?layer;
            pd3:value ?value;
            pd3:id ?id.
            FILTER(?s = """ + '<' + container + '>' + """)
            }
        }
    """
    container_result = fuseki.get_fuseki_data_json(container_query)
    if(len(container_result) > 0):
        for con_result in container_result:
            selected_container_id = con_result["id"]["value"]
            layer = con_result["layer"]["value"]
            value = con_result["value"]["value"]
            con_uri = container.replace(selected_container_id, "")

    # --------------------------------------------------------------
    # container を追加
    # --------------------------------------------------------------
    # contraction
    fuseki_insert_data.append(
        [URIRef(container), pd3.contraction, URIRef(uri)+URIRef(node_id)])

    # output
    fuseki_insert_data.append(
        [URIRef(container), pd3.output, URIRef(uri)+URIRef(node_id)])

    # --------------------------------------------------------------
    # container flowを追加
    # --------------------------------------------------------------
    container_flow_name = "".join(random.choice(
        string.ascii_letters + string.digits) for _ in range(22))
    # RDF.type
    fuseki_insert_data.append([URIRef(con_uri)+URIRef(container_flow_name), \
                            RDF.type, pd3.ContainerFlow])
    # arcType
    fuseki_insert_data.append([URIRef(con_uri)+URIRef(container_flow_name), \
                            pd3.arcType, Literal('hierarchization')])
    # id
    fuseki_insert_data.append([URIRef(con_uri)+URIRef(container_flow_name), \
                            pd3.id, Literal(container_flow_name)])
    # layer
    fuseki_insert_data.append([URIRef(con_uri)+URIRef(container_flow_name), \
                            pd3.layer, Literal(layer)])
    # source
    fuseki_insert_data.append([URIRef(con_uri)+URIRef(container_flow_name), \
                            pd3.source, URIRef(container)])
    # target
    fuseki_insert_data.append([URIRef(con_uri)+URIRef(container_flow_name), \
                            pd3.target, URIRef(uri)+URIRef(node_id)])
    # value
    fuseki_insert_data.append([URIRef(con_uri)+URIRef(container_flow_name), \
                            pd3.value, Literal("")])

    # --------------------------------------------------------------
    # actionのexpansionを追加
    # --------------------------------------------------------------
    fuseki_insert_data.append([URIRef(uri)+URIRef(node_id), \
                            pd3.expansion, URIRef(container)])

    # --------------------------------------------------------------
    # actionのinputを追加
    # --------------------------------------------------------------
    fuseki_insert_data.append([URIRef(uri)+URIRef(node_id), \
                            pd3.input, URIRef(con_uri)+URIRef(container_flow_name)])

    if fuseki.insert(graph_name, fuseki_insert_data):
        # actionのバリューを更新（コンテナ名と一致するため）
        update_query = """
            PREFIX pd3: <http://DigitalTriplet.net/2021/08/ontology#>
            WITH """ + graph_name + """
            DELETE { """ + "<" + uri+node_id + ">" + """ pd3:value """ + '"' + current_item + '"' + """ }
            INSERT { """ + "<" + uri+node_id + ">" + """ pd3:value """ + '"' + value + '"' + """ }
            WHERE {
                """ + "<" + uri+node_id + ">" + """ pd3:value """ + '"' + current_item + '"' + """
            }
        """
        if fuseki.update(update_query):
            messagebox.showinfo("確認", "メンバー関連付け成功しました！", parent=parent)
    else:
        messagebox.showerror("Error", "メンバー関連付け失敗しました！", parent=parent)


def copy_ep_data(graph_name, uri, new_uri, parent):
    """ コンテナ関連付け処理前、プロセスデータをコピー処理

    Args:
        graph_name: グラフ名
        uri: 古uri（ノードuri）
        new_uri: 新uri
        parent: 実行するウィンドウ

    """
    fuseki = fm.FusekiManagement(setting.FUSEKI_URL, setting.FUSEKI_DB)
    update_data_list = {}
    fuseki_insert_data = []

    query = """
        SELECT ?s ?p ?o
        WHERE {
            graph """ + graph_name + """ {
            ?s ?p ?o.
            filter(regex(str(?s),""" + '"' + uri + '"' + """))
            }
        }
    """

    results = fuseki.get_fuseki_data_json(query)
    if(len(results) > 0):
        for result in results:
            subject = result["s"]["value"]
            predicate  = result["p"]["value"]
            object = result["o"]["value"]
            if(subject not in update_data_list.keys()):
                update_data_list[subject] = []
            # 既存のdrive情報をコピーしない
            if(predicate != "http://DigitalTriplet.net/2021/08/ontology#drives"):
                update_data_list[subject].append([predicate, object])

    # dirve情報を追加
    update_data_list[new_uri] = []
    update_data_list[new_uri].append(["http://DigitalTriplet.net/2021/08/ontology#drives", uri])
    
    for copy_node_key in update_data_list.keys():
        for rdf_info in update_data_list[copy_node_key]:
            if(rdf_info[0] == "http://www.w3.org/1999/02/22-rdf-syntax-ns#type") or \
                (rdf_info[0] == "http://DigitalTriplet.net/2021/08/ontology#drives"):
                object = URIRef(rdf_info[1])
            elif(rdf_info[0] == "http://DigitalTriplet.net/2021/08/ontology#attribution") or \
                (rdf_info[0] == "http://DigitalTriplet.net/2021/08/ontology#expansion") or \
                (rdf_info[0] == "http://DigitalTriplet.net/2021/08/ontology#contraction") or \
                (rdf_info[0] == "http://DigitalTriplet.net/2021/08/ontology#output") or \
                (rdf_info[0] == "http://DigitalTriplet.net/2021/08/ontology#input") or \
                (rdf_info[0] == "http://DigitalTriplet.net/2021/08/ontology#member") or \
                (rdf_info[0] == "http://DigitalTriplet.net/2021/08/ontology#source") or \
                    (rdf_info[0] == "http://DigitalTriplet.net/2021/08/ontology#target"):
                object = URIRef(rdf_info[1].replace(uri, new_uri))
            else:
                object = Literal(rdf_info[1])

            node_subject = copy_node_key.replace(uri, new_uri)
            fuseki_insert_data.append([URIRef(node_subject), \
                                    URIRef(rdf_info[0]), object])

    if fuseki.insert(graph_name, fuseki_insert_data) == False:
        messagebox.showerror('Error', 'コピー失敗!', parent=parent)


def copy_container_data(graph_name, uri, container, new_uri, id_list, parent):
    """ コンテナ関連付け処理前、コンテナデータをコピー処理

    Args:
        graph_name: グラフ名
        uri: 古uri（ノードuri）
        container: コンテナ主語（uri+id）
        new_uri: 新uri
        id_list: コンテナのメンバーidリスト
        parent: 実行するウィンドウ

    """
    fuseki = fm.FusekiManagement(setting.FUSEKI_URL, setting.FUSEKI_DB)
    data = data_mg.DataManagement()
    fuseki_insert_data = []

    # memberのrdfデータを取得
    update_data_list = data.get_node_rdf_info(graph_name, uri, id_list)

    # コンテナのrdfデータを取得
    con_subject = "<" + container + ">"
    detail_query_result = data.get_update_detail_data(graph_name, con_subject)

    continaer_id = container.replace(uri,"")
    update_data_list[continaer_id] = []

    if(len(detail_query_result) > 0):
        for result in detail_query_result:
            predicate = result["p"]["value"]
            object = result["o"]["value"]
            if(predicate != "http://DigitalTriplet.net/2021/08/ontology#drives"):
                update_data_list[continaer_id].append([predicate, object])

    # dirve情報を追加
    update_data_list[new_uri] = []
    update_data_list[new_uri].append(["http://DigitalTriplet.net/2021/08/ontology#drives", uri])

    # インサート
    for update_node_id in update_data_list.keys():
        for rdf_info in update_data_list[update_node_id]:
            if(rdf_info[0] == "http://www.w3.org/1999/02/22-rdf-syntax-ns#type"):
                object = URIRef(rdf_info[1])
            elif(rdf_info[0] == "http://DigitalTriplet.net/2021/08/ontology#attribution") or \
                (rdf_info[0] == "http://DigitalTriplet.net/2021/08/ontology#expansion") or \
                (rdf_info[0] == "http://DigitalTriplet.net/2021/08/ontology#contraction") or \
                (rdf_info[0] == "http://DigitalTriplet.net/2021/08/ontology#output") or \
                (rdf_info[0] == "http://DigitalTriplet.net/2021/08/ontology#input") or \
                (rdf_info[0] == "http://DigitalTriplet.net/2021/08/ontology#member") or \
                (rdf_info[0] == "http://DigitalTriplet.net/2021/08/ontology#source") or \
                    (rdf_info[0] == "http://DigitalTriplet.net/2021/08/ontology#target"):
                object = URIRef(rdf_info[1].replace(uri, new_uri))
            # dirve情報を追加
            elif(rdf_info[0] == "http://DigitalTriplet.net/2021/08/ontology#drives"):
                fuseki_insert_data.append([URIRef(new_uri), \
                                    URIRef(rdf_info[0]), URIRef(rdf_info[1])])
                continue
            else:
                object = Literal(rdf_info[1])

            fuseki_insert_data.append([URIRef(new_uri)+URIRef(update_node_id), \
                                    URIRef(rdf_info[0]), object])

    if fuseki.insert(graph_name, fuseki_insert_data) == False:
        messagebox.showerror('Error', '削除失敗!', parent=parent)


def insert_use(graph_name, uri, node_id, log_graph, log_uri, log_node_id):
    """ use関連付け処理で追加するデータを用意

    Args:
        graph_name: グラフ名
        uri: uri
        node_id: 関連付けするGPMノードid
        log_graph: ログフラグ名
        log_uri: ログフラグuri
        log_node_id: ログ関連付けするノードid

    Returns:

    """
    fuseki = fm.FusekiManagement(setting.FUSEKI_URL, setting.FUSEKI_DB)
    fuseki_insert_data_log = []
    fuseki_insert_data_main = []
    pd3 = Namespace("http://DigitalTriplet.net/2021/08/ontology#")

    # ログのUse関連付けを追加
    fuseki_insert_data_log.append([URIRef(log_uri)+URIRef(log_node_id), \
                                pd3.use, URIRef(uri)+URIRef(node_id)])
    # ログプロセスのUse関連付けを追加
    fuseki_insert_data_log.append([URIRef(log_uri), \
                                pd3.use, URIRef(uri)])

    # GPMのUseBy関連付けを追加
    fuseki_insert_data_main.append([URIRef(uri)+URIRef(node_id), \
                                    pd3.useBy, URIRef(log_uri)+URIRef(log_node_id)])
    # GPMプロセスのUse関連付けを追加
    fuseki_insert_data_main.append([URIRef(uri), \
                                    pd3.useBy, URIRef(log_uri)])

    if fuseki.insert(log_graph, fuseki_insert_data_log) and \
            fuseki.insert(graph_name, fuseki_insert_data_main):
        messagebox.showinfo("確認", "Fusekiにインサートしました!")
    else:
        messagebox.showerror("Error", "インサート失敗!")


def delete_use(graph_name, uri, node_id, log_graph, log_uri, log_node_id):
    """ use関連付け削除処理

    Args:
        graph_name: グラフ名
        uri: uri
        node_id: 関連付け削除GPMノードid
        log_graph: ログフラグ名
        log_uri: ログフラグuri
        log_node_id: ログ関連付け削除ノードid

    Returns:

    """
    fuseki = fm.FusekiManagement(setting.FUSEKI_URL, setting.FUSEKI_DB)
    delete_use_data = "<" + uri + node_id + ">"
    query_use = """
        PREFIX pd3: <http://DigitalTriplet.net/2021/08/ontology#>
        WITH """ + log_graph + """
        DELETE { ?s pd3:use """ + delete_use_data + """ }
        WHERE { ?s ?p ?o ; 
                pd3:id """ + '"' + log_node_id + '"' + """. }
    """

    delete_useby_data = "<" + log_uri + log_node_id + ">"
    query_useby = """
        PREFIX pd3: <http://DigitalTriplet.net/2021/08/ontology#>
        WITH """ + graph_name + """
        DELETE { ?s pd3:useBy """ + delete_useby_data + """ }
        WHERE { ?s ?p ?o ; 
                pd3:id """ + '"' + node_id + '"' + """. 
                FILTER(regex(str(?s),""" + '"' + uri + '"' + """))}
    """

    if fuseki.update(query_use) and fuseki.update(query_useby):
        # プロセスuseBy情報を削除するが必要か判断する
        # log_uriのuseBy情報がなければ、プロセスuseByを削除
        useby_list = []
        check_query =  """
            PREFIX pd3: <http://DigitalTriplet.net/2021/08/ontology#>
            SELECT ?useBy
            WHERE {
                graph """ + graph_name + """ {
                ?s ?p pd3:Action;
                pd3:useBy ?useBy.
                FILTER(regex(str(?useBy),""" + '"' + log_uri + '"' + """))
                FILTER(regex(str(?s),""" + '"' + uri + '"' + """))
                }
            }
        """
        results = fuseki.get_fuseki_data_json(check_query)
        if(len(results) > 0):
            for result in results:
                useby_list.append(result["useBy"]["value"])

        # useBy情報がない場合、削除する
        if len(useby_list) == 0:
            query_process_gpm = """
                PREFIX pd3: <http://DigitalTriplet.net/2021/08/ontology#>
                PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                WITH """ + log_graph + """
                DELETE { ?s pd3:use """ + '<' + uri + '>' + """ }
                WHERE { ?s ?p ?o;
                    ?p pd3:EP.
                    FILTER(regex(str(?s),""" + '"' + log_uri + '"' + """))}
            """
            query_process_log = """
                PREFIX pd3: <http://DigitalTriplet.net/2021/08/ontology#>
                WITH """ + graph_name + """
                DELETE { ?s pd3:useBy """ + '<' + log_uri + '>' + """ }
                WHERE { ?s ?p ?o.
                        FILTER(regex(str(?s),""" + '"' + uri + '"' + """))}
            """

            if fuseki.update(query_process_gpm) and fuseki.update(query_process_log):
                messagebox.showinfo("確認", "削除しました！")
            else:
                messagebox.showerror("Error", "削除失敗！")

    else:
        messagebox.showerror("Error", "削除失敗！")