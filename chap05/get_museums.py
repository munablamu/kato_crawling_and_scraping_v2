from SPARQLWrapper import SPARQLWrapper

# SPARQLエンドポイントのURLを指定してインスタンスを作成する。
sparql = SPARQLWrapper('http://ja.dbpedia.org/sparql')
# 日本の美術館を取得するクエリを設定する。
sparql.setQuery(r"""
SELECT * WHERE {
                ?s rdf:type dbo:Museum ;
                prop-ja:所在地 ?address .
                FILTER REGEX(?address, "^\\p{Han}{2,3}[都道府県]")
} ORDER BY ?s
""")
sparql.setReturnFormat('json')
# query()でクエリを実行し、convert()でレスポンスをパースしてdictを得る。
response = sparql.query().convert()

for result in response['results']['bindings']:
    print(result['s']['value'], result['address']['value'])
