import pandas as pd
from apps import es
csv_file = pd.read_csv('products_data.csv')
search_file = pd.concat([csv_file['title'], csv_file['description']], axis = 1)
print(search_file)


index_name = 'fashionshop'
doc_type = 'product'
for i, t in enumerate(search_file['title']):
    s = es.index(index = index_name, doc_type = doc_type, id = i, body = {'title': t})
    print(s)
product = es.get(index= index_name, doc_type = doc_type, id = 10)
print(product)
query = es.search(index = index_name, body={'query':{'match': {'title':'1'}}})
print(query['hits']['total'])
print(query['hits']['hits'])