
import copy
from rdflib import Graph, RDFS, URIRef, Namespace, RDF, Literal

import FusekiManagement as fm
import Association as assoc
import setting

import importlib
importlib.reload(fm)
importlib.reload(assoc)
importlib.reload(setting)

""" データ処理クラス

"""

class DataManagement:
    def __init__(self):
        """ 初期化

        """
        self.fuseki = fm.FusekiManagement(setting.FUSEKI_URL, setting.FUSEKI_DB)


    def get_graph_data_by_ttlfile(self, gpm_uri, node_id_list, object_id_list, selected_edge_id, file_path):
        """ グラフデータを取得

        Args:
            node_id_list: ノードidリスト
            object_id_list: オブジェクトidリスト
            file_path: データを取得するttlフィアルパス

        Returns:
            node_list: ノードリスト（id, node shape, node color）
            edge_list: エッジリスト （soure node, end node, edge color）
            label_list: ラベルリスト
            position: 位置情報

        """
        node_list = []
        edge_list = []
        label_list = {}
        position = {}
        pd3 = Namespace('http://DigitalTriplet.net/2021/08/ontology#')

        with open(file_path, "r", encoding="utf-8") as f:
            g = Graph()
            g.parse(f)

        for s, p, o in g.triples((None, RDF.type, None)):
            # Action
            if(o == pd3.Action and gpm_uri in s):
                for s1, p1, o1 in g.triples((s, pd3.id, None)):
                    id = str(o1)
                    if(id in node_id_list):
                        node_list.append((id, {"s": "o", "color": "tab:blue"}))
                        for s2, p2, o2 in g.triples((s, pd3.geoBoundingX, None)):
                            postion_x = float(o2)
                        for s3, p3, o3 in g.triples((s, pd3.geoBoundingY, None)):
                            postion_y = float(o3)
                        position[id] = [postion_x, 1000-postion_y]
                        for s4, p4, o4 in g.triples((s, pd3.value, None)):
                            value = str(o4)
                            label_list[id] = value
            # Flow
            elif(o == pd3.Flow and gpm_uri in s):
                for s2, p2, o2 in g.triples((s, pd3.source, None)):
                    temp_source = o2
                    for s3, p3, o3 in g.triples((temp_source, pd3.id, None)):
                        source = str(o3)
                for s2, p2, o2 in g.triples((s, pd3.target, None)):
                    temp_target = o2
                    for s3, p3, o3 in g.triples((temp_target, pd3.id, None)):
                        target = str(o3)
                for s2, p2, o2 in g.triples((s, pd3.id, None)):
                    edge_id = str(o2)
                if(source in node_id_list) and (target in node_id_list):
                    if(edge_id == selected_edge_id):
                        edge_list.append((source, target, {"color": "r"}))
                    else:
                        edge_list.append((source, target, {"color": "k"}))

            # object
            elif(o == pd3.Object and gpm_uri in s):
                for s1, p1, o1 in g.triples((s, pd3.id, None)):
                    id = str(o1)
                    if(id in object_id_list):
                        node_list.append((id, {"s": "s", "color": "tab:blue"}))
                        for s2, p2, o2 in g.triples((s, pd3.geoBoundingX, None)):
                            postion_x = float(o2)
                        for s3, p3, o3 in g.triples((s, pd3.geoBoundingY, None)):
                            postion_y = float(o3)
                        position[id] = [postion_x, 1000-postion_y]
                        for s4, p4, o4 in g.triples((s, pd3.value, None)):
                            value = str(o4)
                            label_list[id] = value
                        # action idを取得
                        for s4, p4, o4 in g.triples((s, pd3.output, None)):
                            for s5, p5, o5 in g.triples((o4, pd3.target, None)):
                                for s6, p6, o6 in g.triples((o5, pd3.id, None)):
                                    action = str(o6)
                                    edge_list.append((id, action, {"color": "k"}))

        return node_list, edge_list, label_list, position


    def get_node_value(self, graph, uri, node_id):
        """ ノードバリューを取得

        Args:
            graph: グラフ名
            uri: uri
            node_id: ノードid

        Returns:
            value: ノードバリュー

        """
        query = """
            PREFIX pd3: <http://DigitalTriplet.net/2021/08/ontology#>
            SELECT ?value
            WHERE {
                graph """ + graph + """ {
                ?s pd3:id ?id;
                pd3:value ?value.
                FILTER(?id = """ + '"' + node_id + '"' + """)
                FILTER(regex(str(?s),""" + '"' + uri + '"' + """))
                }
            }
        """
        query_result = self.fuseki.get_fuseki_data_json(query)
        for result in query_result:
            value = result["value"]["value"]

        return value


    def get_graph_containerflow_count(self, graph_name, uri):
        """ グラフにあるコンテナフロー数を取得

        Args:
            graph: グラフ名
            uri: uri

        Returns:
            count: コンテナフロー数

        """
        query = """
            PREFIX pd3: <http://DigitalTriplet.net/2021/08/ontology#>
            SELECT (COUNT(?s) AS ?count)
            WHERE {
                graph """ + graph_name + """ {
                ?s ?p pd3:ContainerFlow;
                pd3:value ?value.
                filter(regex(str(?s),""" + '"' + uri + '"' + """)) 
                }
            }
        """
        query_result = self.fuseki.get_fuseki_data_json(query)
        for result in query_result:
            count = int(result["count"]["value"])

        return count


    def get_ep_container_count(self, graph_name, uri):
        """ EPにあるコンテナ数を取得

        Args:
            graph: グラフ名
            uri: uri

        Returns:
            count: コンテナ数

        """
        count = 0
        query = """
            PREFIX pd3: <http://DigitalTriplet.net/2021/08/ontology#>
            SELECT (COUNT(?s) AS ?count)
            WHERE {
                graph """ + graph_name + """ {
                ?s ?p pd3:Container;
                    pd3:value ?value.
                filter(regex(str(?s),""" + '"' + uri + '"' + """)) 
                }
            }
        """
        query_result = self.fuseki.get_fuseki_data_json(query)
        if(len(query_result) > 0):
            for result in query_result:
                count = int(result["count"]["value"])

        return count


    def get_container_member(self, graph_name, uri, container):
        """ コンテナメンバーを取得

        Args:
            graph_name: グラフ名
            uri: コンテナuri
            container: コンテナ主語（uri+id）

        Returns:
            node_list: 取得メンバー名リスト
            id_list: 取得メンバーidリスト

        """
        node_list = {}
        id_list = {}
        node_list["top"] = []
        id_list["top"] = []

        query_result = self.get_container_member_query(graph_name, \
                        container, uri)

        for result in query_result:
            value = result["value"]["value"]
            id = result["id"]["value"]
            node_list["top"].append(value)
            id_list["top"].append(id)

        container_count = self.get_ep_container_count(graph_name, uri)

        if(container_count != 0):
            (node_list, id_list) = self.get_member_by_fuseki(graph_name, uri, \
                                                    container_count, \
                                                    False, node_list, id_list)

        return node_list, id_list


    def get_member_by_fuseki(self, graph_name, uri, count, end, node_list, id_list):
        """ Fusekiからメンバーを取得

        Args:
            graph_name: グラフ名
            uri: uri
            count: コンテナ数
            end: 取得最後か判断フラグ
            node_list: 取得メンバー名リスト
            id_list: 取得メンバーidリスト

        Returns:

        """
        if(count == 0) or (end == True):
            return node_list, id_list

        node_list_copy = copy.copy(node_list)

        for key in node_list_copy.keys():
            for index, item in enumerate(node_list_copy[key]):
                query = """
                PREFIX pd3: <http://DigitalTriplet.net/2021/08/ontology#>
                SELECT ?s
                WHERE {
                        graph """ + graph_name + """ {
                            ?s ?p pd3:Container;
                            pd3:value ?value.
                        FILTER(?value = """ + '"' + item + '"' + """ )
                        FILTER(regex(str(?s),""" + '"' + uri + '"' + """)) 
                        }
                }
                """
                query_result = self.fuseki.get_fuseki_data_json(query)
                if(len(query_result) > 0):
                    if(item not in node_list.keys()):
                        node_list[item] = []
                        id_list[item] = []
                        count -= 1
                        for result in query_result:
                            container = result["s"]["value"]

                        query_2 = """
                            PREFIX pd3: <http://DigitalTriplet.net/2021/08/ontology#>
                            SELECT ?id ?value
                            WHERE {
                                    graph """ + graph_name + """ {
                                    ?s ?p pd3:Action;
                                    pd3:attribution ?parent;
                                    pd3:id ?id;
                                    pd3:value ?value.
                                FILTER(?parent = <""" + container + """> )
                                FILTER(regex(str(?s),""" + '"' + uri + '"' + """))
                                }
                            }
                        """
                        query_result = self.fuseki.get_fuseki_data_json(query_2)
                        for result in query_result:
                            value = result["value"]["value"]
                            id = result["id"]["value"]
                            node_list[item].append(value)
                            id_list[item].append(id)
                        return self.get_member_by_fuseki(graph_name, uri, count, \
                                                    end, node_list, id_list)

        end = True
        return self.get_member_by_fuseki(graph_name, uri, count, end, node_list, id_list)


    def get_member(self, count, end, uri_node_list, uri_node_id_list, node_list, \
        id_list):
        """ ツリーデータからメンバーを取得

        Args:
            count: コンテナ数
            end: 取得最後か判断フラグ
            uri_node_list: 参照する用ノード名リスト
            uri_node_id_list: 参照する用ノードidリスト
            node_list: 結果ノード名リスト
            id_list: 結果ノードidリスト

        Returns:

        """
        if (count == 0) or (end == True):
            return node_list, id_list

        node_id_list = copy.copy(id_list)

        for key in node_id_list.keys():
            for index, node_id in enumerate(node_id_list[key]):
                if(node_id in uri_node_id_list.keys()):
                    node_value = node_list[key][index]

                    if(node_value not in node_list.keys()):
                        count -= 1
                        node_list[node_value] = copy.copy(uri_node_list[node_id])
                        id_list[node_value] = copy.copy(uri_node_id_list[node_id])

                        return self.get_member(count, end, uri_node_list, uri_node_id_list, \
                            node_list, id_list)
        end = True
        return self.get_member(count, end, uri_node_list, uri_node_id_list, node_list, id_list)


    def get_top_node_list_in_graph(self, selected_graph_name):
        """ グラフに階層Topノード(アクション)を取得

        Args:
            selected_graph_name: グラフ名

        Returns:
            node_id_list: Topノードリスト

        """
        # 最上層アクションを取得
        query = """
            PREFIX pd3: <http://DigitalTriplet.net/2021/08/ontology#>
            SELECT ?id ?value
            WHERE {
                graph """ + selected_graph_name + """ {
                ?s ?p pd3:Action;
                    pd3:id ?id;
                    pd3:value ?value.
                FILTER NOT EXISTS {?s pd3:attribution ?parent}
                }
            }
        """

        node_id_list = {}
        node_id_list["top"] = []

        query_result = self.fuseki.get_fuseki_data_json(query)
        for result in query_result:
            value = result["value"]["value"]
            id = result["id"]["value"]
            # コンテナ関連付けする時、新URIにidをコピーするため
            if(id not in node_id_list["top"]):
                node_id_list["top"].append(id)

        return node_id_list


    def get_top_node_list_in_uri(self, selected_graph_name, uri):
        """ グラウに特定URIにある階層Topノード(アクション)を取得

        Args:
            selected_graph_name: グラフ名
            uri: 指定uri

        Returns:
            node_id_list: Topノードリスト

        """
        # 最上層アクションを取得
        query = """
            PREFIX pd3: <http://DigitalTriplet.net/2021/08/ontology#>
            SELECT ?id ?value
            WHERE {
                graph """ + selected_graph_name + """ {
                ?s ?p pd3:Action;
                    pd3:id ?id;
                    pd3:value ?value.
                FILTER NOT EXISTS {?s pd3:attribution ?parent}
                FILTER(regex(str(?s),""" + '"' + uri + '"' + """)) 
                }
            }
        """

        node_id_list = {}
        node_id_list["top"] = []

        query_result = self.fuseki.get_fuseki_data_json(query)
        for result in query_result:
            value = result["value"]["value"]
            id = result["id"]["value"]
            # コンテナ関連付けする時、新URIにidをコピーするため
            if(id not in node_id_list["top"]):
                node_id_list["top"].append(id)

        return node_id_list


    def get_top_level_object_list(self, selected_graph_name, selected_uri):
        """ 選択したプロセスに階層Topオブジェクトを取得

        Args:
            selected_graph_name: グラフ名
            uri: 指定uri

        Returns:
            object_list: オブジェクトバリューリスト
            object_id_list: オブジェクトidリスト

        """
        # 最上層オブジェクトを取得
        query = """
            PREFIX pd3: <http://DigitalTriplet.net/2021/08/ontology#>
            SELECT ?s ?id ?value
            WHERE {
                graph """ + selected_graph_name + """ {
                ?s ?p pd3:Object;
                    pd3:id ?id;
                    pd3:value ?value.
                FILTER NOT EXISTS {?s pd3:attribution ?parent}
                }
            }
        """
        object_id_list = {}
        object_id_list["top"] = []
        object_list = {}
        object_list["top"] = []

        query_result = self.fuseki.get_fuseki_data_json(query)
        if(len(query_result) > 0):
            for result in query_result:
                subject = result["s"]["value"]
                id = result["id"]["value"]
                value = result["value"]["value"]
                uri = subject.replace(id, "")
                if(uri == selected_uri):
                    object_id_list["top"].append(id)
                    object_list["top"].append(value)

        return object_list, object_id_list


    def get_top_level_edge_list(self, selected_graph_name, selected_uri):
        """ 選択したプロセスに階層Top levelエッジを取得

        Args:
            selected_graph_name: グラフ名
            uri: 指定uri

        Returns:
            edge_list: オブジェクトバリューリスト
            edge_id_list: オブジェクトidリスト

        """
        # 最上層エッジを取得
        query = """
            PREFIX pd3: <http://DigitalTriplet.net/2021/08/ontology#>
            SELECT ?id ?value
            WHERE {
                graph """ + selected_graph_name + """ {
                ?s ?p pd3:Action;
                    pd3:output ?output.
                FILTER NOT EXISTS {?s pd3:attribution ?parent}
                FILTER(regex(str(?s),""" + '"' + selected_uri + '"' + """)) 
                graph """ + selected_graph_name + """ {
                    ?output pd3:value ?value;
                    pd3:id ?id.
                }
            }
        }
        """

        edge_id_list = {}
        edge_id_list["top"] = []
        edge_list = {}
        edge_list["top"] = []

        query_result = self.fuseki.get_fuseki_data_json(query)
        if(len(query_result) > 0):
            for result in query_result:
                id = result["id"]["value"]
                value = result["value"]["value"]
                edge_id_list["top"].append(id)
                edge_list["top"].append(value)

        return edge_list, edge_id_list


    def get_node_info(self, graph_name, node_id):
        """ ノード情報を取得

        Args:
            graph_name: グラフ名
            node_id: ノードid

        Returns:
            id: id情報
            action: actionType情報
            layer: layer情報

        """
        query = """
            PREFIX pd3: <http://DigitalTriplet.net/2021/08/ontology#>
            PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            select distinct ?s ?id ?actionType ?height ?width ?pos_x ?pos_y ?layer ?type
            where {
                graph """ + graph_name + """ 
                {
                    ?s pd3:id ?id;
                    pd3:actionType ?actionType;
                    pd3:geoBoundingHeight ?height;
                    pd3:geoBoundingWidth ?width;
                    pd3:geoBoundingX ?pos_x;
                    pd3:geoBoundingY ?pos_y;
                    pd3:layer ?layer;
                    rdf:type ?type.
                }
                FILTER(?id = """ + '"' + node_id + '"' + """)
            }
        """

        query_result = self.fuseki.get_fuseki_data_json(query)
        for result in query_result:
            id = result["id"]["value"]
            action = result["actionType"]["value"]
            layer = result["layer"]["value"]

        return id, action, layer


    def get_use_info(self, graph_name, node_uri, node_id):
        """ ノードUse, UseBy情報を取得

        Args:
            graph_name: グラフ名
            node_uri: ノードuri
            node_id: ノードid

        Returns:
            use: use情報
            useBy: useBy情報

        """
        useby = []
        use = []
        query_use = """
            PREFIX pd3: <http://DigitalTriplet.net/2021/08/ontology#>
            PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            select distinct ?s ?id ?use
            where {
                graph """ + graph_name + """ {
                ?s pd3:id ?id;
                pd3:use ?use.
                }
                FILTER(?id = """ + '"' + node_id + '"' + """)
            }
        """

        query_use_result = self.fuseki.get_fuseki_data_json(query_use)
        if(len(query_use_result) > 0):
            for result in query_use_result:
                use.append(result["use"]["value"])

        query_useby = """
            PREFIX pd3: <http://DigitalTriplet.net/2021/08/ontology#>
            PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            select distinct ?s ?id ?useby
            where {
                graph """ + graph_name + """ {
                ?s pd3:id ?id;
                pd3:useBy ?useby.
                }
                FILTER(?id = """ + '"' + node_id + '"' + """)
                FILTER(regex(str(?s),""" + '"' + node_uri + '"' + """))
            }
        """

        query_useby_result = self.fuseki.get_fuseki_data_json(query_useby)
        if(len(query_useby_result) > 0):
            for result in query_useby_result:
                useby.append(result["useby"]["value"])

        return use, useby


    def get_node_subject_info(self, graph_name, node_id):
        """ Fusekiにノードの主語を取得

        Args:
            graph_name: グラフ名
            node_id: ノードid

        Returns:
            target: ノード主語（フォーマット：<uri+id>）

        """
        target = None
        query = """
            PREFIX pd3: <http://DigitalTriplet.net/2021/08/ontology#>
            SELECT ?s
            WHERE {
                graph """ + graph_name + """ {
                    ?s pd3:id ?id.
                FILTER(?id = """ + '"' + node_id + '"' + """)
                }
            }
        """
        query_result = self.fuseki.get_fuseki_data_json(query)
        if(len(query_result) > 0):
            for result in query_result:
                target = result["s"]["value"]

            target = "<" + target + ">"

        return target


    def get_supplement_detail_info(self, graph_name, type, target_node):
        """ ノード補足情報を取得

        Args:
            graph_name: グラフ名
            type: ノードのtype（オブジェクト, オブジェクト以外）
            target_node: ノード（uri+id）

        Returns:
            id: ノードid
            value:  ノードバリュー

        """
        # オブジェクトではない場合
        if(type != ""):
            type = '"' + type + '"'

            query = """
                PREFIX pd3: <http://DigitalTriplet.net/2021/08/ontology#>
                SELECT ?s ?id ?value
                WHERE {
                    graph """ + graph_name + """ {
                        ?s pd3:target ?target;
                        pd3:arcType ?arcType;
                        pd3:id ?id;
                        pd3:value ?value.
                    FILTER(?arcType = """ + type + """)
                    FILTER(?target = """ + target_node + """)
                    }
                }
            """
            results = self.fuseki.get_fuseki_data_json(query)
            if(len(results) > 0):
                for result in results:
                    subject = result["s"]["value"]
                    id = result["id"]["value"]
                    value = result["value"]["value"]

                return id, value

        # オブジェクトの場合
        else:
            object_id = {}
            object_value = {}
            supflow_sub = []
            # オブジェクトと繋がってるsupflowを取得
            query_supflow = """
                PREFIX pd3: <http://DigitalTriplet.net/2021/08/ontology#>
                SELECT ?s 
                WHERE {
                    graph """ + graph_name + """ {
                        ?s pd3:target ?target;
                        pd3:arcType ?arcType;
                        pd3:id ?id;
                        pd3:value ?value.
                    FILTER(?arcType = "tool/knowledge")
                    FILTER(?target = """ + target_node + """)
                    }
                }
            """
            query_supflow_results = self.fuseki.get_fuseki_data_json(query_supflow)
            if(len(query_supflow_results) > 0):
                for result in query_supflow_results:
                    supflow_sub.append(result["s"]["value"])

                object_id[target_node] = []
                object_value[target_node] = []

                for subject in supflow_sub:
                    subject = "<" + subject + ">"
                    object_query = """
                        PREFIX pd3: <http://DigitalTriplet.net/2021/08/ontology#>
                        SELECT ?id ?value
                        WHERE {
                            graph """ + graph_name + """ {
                                ?s ?p pd3:Object;
                                pd3:output ?output;
                                pd3:id ?id;
                                pd3:value ?value.
                            FILTER(?output = """ + subject + """)
                            }
                        }
                    """
                    object_result = self.fuseki.get_fuseki_data_json(object_query)
                    if(len(object_result) > 0):
                        for result in object_result:
                            object_id[target_node].append(result["id"]["value"])
                            object_value[target_node].append(
                                result["value"]["value"])

                return object_id, object_value

        return None, None


    def get_node_uri(self, graph, node_id):
        """ 選択したノードのuriを取得

        Args:
            graph: グラフ名
            node_id: ノードid

        Returns:
            node_uri: ノードuri

        """
        query = """
            PREFIX pd3: <http://DigitalTriplet.net/2021/08/ontology#>
            SELECT ?s ?id
            WHERE {
                graph """ + graph + """ {
                ?s pd3:id ?id.
                FILTER(?id = """ + '"' + node_id + '"' + """)
                }
            }
        """
        query_result = self.fuseki.get_fuseki_data_json(query)
        for result in query_result:
            subject = result["s"]["value"]
            id = result["id"]["value"]
            node_uri = subject.replace(id, "")

        return node_uri


    def get_update_detail_data(self, graph_name, subject):
        """ ノードの詳細データを取得

        Args:
            graph_name: グラフ名
            subject: 取得する対象ノード主語

        Returns:
            取得json結果

        """
        query = """
            PREFIX pd3: <http://DigitalTriplet.net/2021/08/ontology#>
            SELECT ?p ?o
            WHERE {
                graph """ + graph_name + """ {
                """ + subject + """ ?p ?o.
                }
            }
        """
        return self.fuseki.get_fuseki_data_json(query)


    def get_node_rdf_info(self, graph_name, uri, id_list):
        """ ノードのRDF情報を取得

        Args:
            graph_name: グラフ名
            uri: uri
            id_list: ノードidリスト

        Returns:
            update_data_list: 取得したデータリスト

        """
        update_data_list = {}

        for key in id_list.keys():
            for member in id_list[key]:
                action_subject = "<" + uri + member + ">"
                update_data_list[member] = []
                # Flow更新データを取得
                flow_query = """
                PREFIX pd3: <http://DigitalTriplet.net/2021/08/ontology#>
                    SELECT distinct ?id
                    WHERE {
                        graph """ + graph_name + """ {
                            ?s ?p pd3:Flow;
                            pd3:id ?id;
                            pd3:source ?source;
                            pd3:target ?target.
                        FILTER((?source = """ + action_subject + """) || 
                                (?target = """ + action_subject + """))
                        }
                    }
                """
                flow_id = []
                flow_result = self.fuseki.get_fuseki_data_json(flow_query)
                if(len(flow_result) > 0):
                    for result in flow_result:
                        flow_id.append(result["id"]["value"])

                    # Flow詳細データを取得と更新
                    for id in flow_id:
                        flow_subject = "<" + uri + id + ">"
                        update_data_list[id] = []

                        flow_detail_query_result = self.get_update_detail_data(
                            graph_name, flow_subject)
                        if(len(flow_detail_query_result) > 0):
                            for result in flow_detail_query_result:
                                predicate = result["p"]["value"]
                                object = result["o"]["value"]
                                update_data_list[id].append([predicate, object])

                # supFlow
                supflow_query = """
                PREFIX pd3: <http://DigitalTriplet.net/2021/08/ontology#>
                    SELECT distinct ?id
                    WHERE {
                        graph """ + graph_name + """ {
                            ?s ?p pd3:SupFlow;
                            pd3:id ?id;
                            pd3:target ?target.
                        FILTER(?target = """ + action_subject + """)
                        }
                    }
                """
                supflow_id = []
                supflow_result = self.fuseki.get_fuseki_data_json(supflow_query)
                if(len(supflow_result) > 0):
                    for result in supflow_result:
                        supflow_id.append(result["id"]["value"])

                    # SupFlow詳細データを取得と更新
                    for id in supflow_id:
                        supflow_subject = "<" + uri + id + ">"
                        update_data_list[id] = []

                        supflow_detail_query_result = self.get_update_detail_data(
                            graph_name, supflow_subject)
                        if(len(supflow_detail_query_result) > 0):
                            for result in supflow_detail_query_result:
                                predicate = result["p"]["value"]
                                object = result["o"]["value"]
                                # objectと繋がる場合、object処理
                                if(predicate == "http://DigitalTriplet.net/2021/08/ontology#value") and \
                                (object == ""):
                                    object_update_data = assoc.change_object_uri(graph_name, uri, \
                                                                            supflow_subject)
                                    update_data_list.update(object_update_data)
                                update_data_list[id].append([predicate, object])

                # Action更新データを取得
                query_results = self.get_update_detail_data(graph_name, action_subject)
                if(len(query_results) > 0):
                    for result in query_results:
                        predicate = result["p"]["value"]
                        object = result["o"]["value"]
                        update_data_list[member].append([predicate, object])

                if(key != "top"):
                    # Container更新データを取得
                    con_query = """
                    PREFIX pd3: <http://DigitalTriplet.net/2021/08/ontology#>
                        SELECT distinct ?id
                        WHERE {
                            graph """ + graph_name + """ {
                                ?s ?p pd3:Container;
                                pd3:id ?id;
                                pd3:value ?value.
                            FILTER(?value = """ + '"' + key + '"' + """)
                            }
                        }
                    """
                    con_result = self.fuseki.get_fuseki_data_json(con_query)
                    if(len(con_result) > 0):
                        for result in con_result:
                            container_id = result["id"]["value"]

                        # object詳細データを取得と更新
                        container_subject = "<" + uri + container_id + ">"
                        update_data_list[container_id] = []

                        container_detail_query_result = self.get_update_detail_data(
                            graph_name, container_subject)
                        if(len(container_detail_query_result) > 0):
                            for result in container_detail_query_result:
                                predicate = result["p"]["value"]
                                object = result["o"]["value"]
                                update_data_list[container_id].append([predicate, object])

                    # ContainerFlow更新データを取得
                    conflow_query = """
                    PREFIX pd3: <http://DigitalTriplet.net/2021/08/ontology#>
                        SELECT distinct ?id
                        WHERE {
                            graph """ + graph_name + """ {
                                ?s ?p pd3:ContainerFlow;
                                pd3:id ?id;
                                pd3:source ?source.
                            FILTER(?source = """ + container_subject + """)
                            }
                        }
                    """
                    conflow_result = self.fuseki.get_fuseki_data_json(conflow_query)
                    if(len(conflow_result) > 0):
                        for result in conflow_result:
                            container_flow_id = result["id"]["value"]

                        # ContainerFlow詳細データを取得と更新
                        container_flow_subject = "<" + uri + container_flow_id + ">"
                        update_data_list[container_flow_id] = []

                        container_flow_detail_query_result = self.get_update_detail_data(
                            graph_name, container_flow_subject)
                        if(len(container_flow_detail_query_result) > 0):
                            for result in container_flow_detail_query_result:
                                predicate = result["p"]["value"]
                                object = result["o"]["value"]
                                update_data_list[container_flow_id].append(
                                    [predicate, object])

        return update_data_list


    def get_container_query(self, graph, target):
        """ コンテナ情報を取得

        Args:
            graph: グラフ名
            target: targetノード情報(uri+id)

        Returns:
            検索結果

        """
        query = """
            PREFIX pd3: <http://DigitalTriplet.net/2021/08/ontology#>
            SELECT ?source
            WHERE {
                graph """ + graph + """ {
                ?s ?p pd3:ContainerFlow;
                    pd3:source ?source;
                    pd3:target ?target.
                FILTER(?target = <""" + target + """> )
                }
            }
        """

        return self.fuseki.get_fuseki_data_json(query)


    def get_container_member_query(self, graph, container, uri):
        """ コンテナメンバー情報を取得

        Args:
            graph: グラフ名
            container: コンテナ情報(主語)
            uri: uri情報

        Returns:
            検索結果

        """
        query = """
            PREFIX pd3: <http://DigitalTriplet.net/2021/08/ontology#>
            SELECT ?id ?value
            WHERE {
                graph """ + graph + """ {
                ?s ?p pd3:Action;
                    pd3:attribution ?parent;
                    pd3:id ?id;
                    pd3:value ?value.
                FILTER(?parent = <""" + container + """> )
                FILTER(regex(str(?s),""" + '"' + uri + '"' + """)) 
                }
            }
        """

        return self.fuseki.get_fuseki_data_json(query)


    def get_container_edge_query(self, graph, container, uri):
        """ コンテナにあるエッジ情報を取得

        Args:
            graph: グラフ名
            container: コンテナ情報(主語)
            uri: uri情報

        Returns:
            検索結果

        """
        query = """
            PREFIX pd3: <http://DigitalTriplet.net/2021/08/ontology#>
            SELECT ?id ?value
            WHERE {
                graph """ + graph + """ {
                ?s ?p pd3:Action;
                    pd3:attribution ?parent;
                    pd3:output ?output.
                FILTER(?parent = <""" + container + """> )
                FILTER(regex(str(?s),""" + '"' + uri + '"' + """)) 
                graph """ + graph + """ {
                    ?output pd3:value ?value;
                    pd3:id ?id.
                }
            }
        }
        """

        return self.fuseki.get_fuseki_data_json(query)


    def get_obejct_in_container_query(self, graph, container, uri):
        """ コンテナにあるオブジェクト情報を取得

        Args:
            graph: グラフ名
            container: コンテナ情報(主語)
            uri: uri情報

        Returns:
            検索結果

        """
        query = """
            PREFIX pd3: <http://DigitalTriplet.net/2021/08/ontology#>
            SELECT ?id ?value
            WHERE {
                graph """ + graph + """ {
                ?s ?p pd3:Object;
                    pd3:attribution ?parent;
                    pd3:id ?id;
                    pd3:value ?value.
                FILTER(?parent = <""" + container + """> )
                FILTER(regex(str(?s),""" + '"' + uri + '"' + """)) 
                }
            }
        """

        return self.fuseki.get_fuseki_data_json(query)


    def get_node_subject_id_query(self, graph, node_id):
        """ ノード主語とid情報を取得

        Args:
            graph: グラフ名
            node_id: ノードd

        Returns:
            検索結果

        """
        query = """
            PREFIX pd3: <http://DigitalTriplet.net/2021/08/ontology#>
            SELECT ?s ?id
            WHERE {
                graph """ + graph + """ {
                ?s ?p pd3:Action;
                    pd3:id ?id.
                FILTER(?id = """ + '"' + node_id + '"' + """)
                }
            }
        """

        return self.fuseki.get_fuseki_data_json(query)
