# estimador del valor bursátil de las empresas del sp500

# Gathering
### notebooks/gather.ipynb
- Se ha obtenido de <a href="https://en.wikipedia.org/wiki/List_of_S%26P_500_companies">wikipedia</a> una tabla con todas las compañias que forman parte del sp500. También una tabla con sus miembros históricos.
- de <a href="https://github.com/fja05680/sp500">este repositorio</a> se ha obtenido un csv con fechas de todos los miembros del sp500 desde 1996
- a partir de ambas fuentes se han construido dos tablas, una con todos los miembros históricos y otra con todos los movimientos.
- A partir de la tabla anterior, se ha intentado llamar a <a href="https://site.financialmodelingprep.com/developer/docs/">esta API</a> para obtener los estados financieros y la capitalización bursátil de las empresas. 
- De esa API también, se han obtenido también los datos del Market Capitalization diarios de las compañias del sp500.
- También se ha utilizado <a href="https://fred.stlouisfed.org/">esta API</a> para obtener datos como la inflación en USA y así ajustar nuestros valores. También se va a usar esa API para obtener valores de otra series relativas a la coyuntura económica de Estados Unidos

# Cleaning
### notebooks/clean.ipynb
- Se han construido las dos tablas mencionadas anteriormente que incluyen a las compañias del sp500
- Se han unido todos los estados financieros en una unica tabla. Se han convertido las variables numericas a miles de millones y se ha ajustado a la inflación.
- Se ha obtenido la variable target (media móvel del market cap 10 dias despues de publicar resultados) y se ha unido a la tabla anterior de los estados financieros

# Model Build
## Benchmark
- Debido a que el numero inicial de variables es elevado (120) y existe mucha multiclonearidad, se han cogido todas las variables y se ha entrenado un algoritmo XGBoost de regresión que optimiza el error cuadrático medio con el objetivo de obtener
una intuición sobre que variables son las mas importantes. Se obtiene que el beneficio neto (netIncome) y otras variables relacionadas con el son las que mas importan a la hora de predecir el modelo, lo cual. Posteriormente se han creado nuevos features a partir de ratios financieros y de inccrementos a´nuales de variables que se consideraban relevantes. Se ha vuelto a entrenar y se ha obtenido un mse de 1800, o un rmse de 40, este valor no es bueno, pero muchas multicolinearidades han desaparecido. El objetivo ahora es coger las variables más importantes y hacer un análisis exploratorio, ver que variables originales correlan poco con ellas y añadirlas

