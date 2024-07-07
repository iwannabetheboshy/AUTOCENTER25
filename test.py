from requests import get
from datetime import datetime

s = datetime.now()
print(get('http://78.46.90.228/api/?ip=127.0.0.1&code=A25nhGfE56Kd&sql=select+*+from+main+WHERE+1+=+1+and+AUCTION+NOT+LIKE+"%USS%"+and+YEAR+>=+2015+and+FINISH+>=+1').text)
print(datetime.now()-s)