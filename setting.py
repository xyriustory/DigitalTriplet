import configparser

""" 設定ファイルから設定内容を読み込む

"""

FUSEKI_URL = ""
FUSEKI_DB = ""

FUSEKI_ID = ""
FUSEKI_PW = ""

NEO4J_URI = ""
NEO4J_USER = ""
NEO4J_PW = ""

# 設定ファイルの読み込み
config = configparser.ConfigParser()
config.read('settings.ini', encoding='utf-8')

# fuseki設定内容を取得
FUSEKI_URL = config.get('FUSEKI', 'url')
FUSEKI_DB = config.get('FUSEKI', 'database')

# fusekiアクセス権限設定を取得
FUSEKI_ID = config.get('FUSEKI', 'account')
FUSEKI_PW = config.get('FUSEKI', 'password')

# Neo4j設定を取得
NEO4J_URI = config.get('NEO4J', 'uri')
NEO4J_USER = config.get('NEO4J', 'user')
NEO4J_PW = config.get('NEO4J', 'password')

