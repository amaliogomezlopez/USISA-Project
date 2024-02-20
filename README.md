<br/>
<p align="center">
  <a href="https://github.com/amaliogomezlopez/USISA Project">
    <img src="https://www.usisa.com/wp-content/themes/usisa_theme/images/logo-usisa.svg" alt="Logo" width="80" height="80">
  </a>

  <h3 align="center">USISA Project by Amalio</h3>
    Clustering project for marketing campaign. Sales prediction using timeseries and recommendation system.
    <br/>
    <br/>
    <a href="https://github.com/amaliogomezlopez/USISA Project"><strong>Explore the docs »</strong></a>
    <br/>
    <br/>
    <a href="https://github.com/amaliogomezlopez/USISA Project">View Demo</a>
    .
    <a href="https://github.com/amaliogomezlopez/USISA Project/issues">Report Bug</a>
    .
    <a href="https://github.com/amaliogomezlopez/USISA Project/issues">Request Feature</a>
  </p>
</p>

![usisa_barco](https://github.com/AndresMembrillo/proyecto-usisa/assets/145653361/d019eb2f-299d-4f14-b5c2-a1bae1c6bb58)

## Table Of Contents

* [About the Project](#about-the-project)
* [Built With](#built-with)
* [Usage](#usage)
* [Authors](#authors)
* [Acknowledgements](#acknowledgements)

## About The Project

<a href="https://ibb.co/Wzqmvyy"><img src="https://i.ibb.co/xgPxqjj/piechart.png" alt="piechart" border="0" width="400"></a>

## 1-Introducción
El proyecto trata acerca de datos de una empresa llamada USISA (Unión Salazonera Isleña
S. A.). Ubicada en Isla Cristina (Huelva) y con más de 40 años en la industria, es la
conservera más grande de Andalucía.

La empresa tiene como objetivo mejorar los números de venta de su tienda online. Para ello
se propone ofrecer una campaña de ofertas a un grupo concreto de clientes, porque no es
viable en cuanto a recursos alcanzar al total de clientes.
Diferenciar y agrupar los clientes es la piedra angular del proyecto. Se trata de caracterizar
a estos clientes por sus hábitos de compra. Se tiene en cuenta la frecuencia de compra, lo
reciente que han comprado y el dinero que han gastado.

## 2-Objetivos
2.1- Principal
El proyecto busca dar respuesta a la pregunta anteriormente desarrollada para concluir el
grupo óptimo de clientes (así como un modelo que los identifique) para ofrecer una
campaña de ofertas. Los grupos tienen que estar correctamente definidos y tiene que tener
sentido las variables que caracterizan a cada uno.
La hipótesis inicial es que, siguiendo el sentido común, los clientes más habituales que
realizan muchos pedidos y gastan mucho dinero serían más interesantes para enfocar la
campaña. Al contrario que a un grupo de clientes perdido del que se puede recuperar un
porcentaje.

2.2-Secundarios
Uno de los objetivos secundarios es la agrupación de productos. Comprobar las
combinaciones de productos que realizan los clientes por pedido individual. El propósito de
esto es ver si existe algún patrón en la compra.
El segundo objetivo secundario es un sistema de recomendación que se sugiere para
implementar la campaña de ofertas. En lugar de ofrecer descuentos directos sobre el precio
final en tienda. Se sugiere ofrecer descuentos en productos específicos que el algoritmo
sugiere a los clientes. El objetivo de esto sería incentivar aún más la compra al mismo
tiempo que se recuperan clientes o se establece un programa de fidelización en función del
resultado del clustering en el objetivo principal.

## Built With

Los datos de la base de datos en SQL fueron extraídos usando MySQL. Para el análisis y realización del proyecto se uso:
-Visualización: Seaborn, Matplot, Geopy.
-Modelos: Pandas, Scikit
-Sistema de recomendación: Surprise

## Conclusiones

El proyecto busca aumentar el número de ventas y realizar un programa de fidelización. Para ello se dividen e identifican correctamente los clientes a los que ofrecer una campaña de ofertas.
Aquí podemos ver la distribución de los clusters y las variables que los explican:


<a href="https://imgbb.com/"><img src="https://i.ibb.co/X8xF6Ym/cluster3d.png" alt="cluster3d" border="0"></a>

Del mismo modo añadimos un gráfico mostrando la distribución del dinero gastado por cada grupo de clentes:
<a href="https://ibb.co/vHNf1GK"><img src="https://i.ibb.co/bP4Y1Z8/dinerocluster.png" alt="dinerocluster" border="0"></a>

Conclusiones del proyecto:

🟢Identificados correctamente los clusters

🟢Explicación y justificación de cada grupo de clientes

🟢El análisis de los datos indican mucha rotación de clientes. Los clientes no realizan demasiados pedidos, una de las razonnes es porque los productos son conservas

🟢No existen datos de valoraciones lo que dificulta la implementación de un correcto sistema de recomendación

🟢Predicción de ventas 1 y 3 meses a futuro

Futuras líneas de investigación:
🟨Churn

🟨Análisis productos en carrito de compra

🟨Sistema de recomendación

## Authors

* **Amalio Gómez López** - *Data Scientist* - [Amalio Gómez López](https://github.com/amaliogomezlopez/) - *USISA Project*

## Acknowledgements

* [Amalio Gómez López](https://github.com/amaliogomezlopez/)
* [Linkedin Profile](https://www.linkedin.com/in/amaliogomezlopez/)
* [Portfolio Website](https://amaliogomezlopez.com/)
