#!/usr/bin/env python
# coding: utf-8

import pandas as pd
import re
import numpy as np
import datetime
from unidecode import unidecode
import warnings
warnings.filterwarnings('ignore')
from statsmodels.tsa.seasonal import seasonal_decompose
#FUNCIONES
from funciones_usisa import *
#VISUALIZACION
import matplotlib.pyplot as plt
import seaborn as sns
#MODELOS
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler


df_new = pd.read_csv("tienda_online_nuevo.csv", encoding='ISO-8859-1')
df_antiguo = pd.read_excel("tienda_online_antiguo.xlsx")



# FUNCIONES PARA DF_NUEVO

#MANTENEMOS LAS COLUMNAS DESEADAS Y NOS DESHACEMOS DEL RESTO
def tirar_columnas_nuevo_email_postal(x):  
    quedar = ['order_number', "billing_first_name", "billing_last_name", "status",'order_date', 'billing_postcode',         'billing_city', 'billing_email']

    quedar.extend([f'line_item_{i}' for i in range(1, 34)])

    return x[quedar]

#DESGLOSAR LOS DIFERENTES PRODUCTOS DE CADA PEDIDO EN UNA FILA INDEPENDIENTE MANTENIENDO EL RESTO DE DATOS 
def desglosar_items(x):
    columnas_items=[f'line_item_{i}' for i in range(1,34)]
    resto_columnas=['billing_first_name', 'billing_last_name', 'order_date',
       'order_number', "status", 'billing_postcode', 'billing_city', 'billing_email']

    df_melted = pd.melt(x, id_vars=resto_columnas, value_vars=columnas_items, var_name='line_item')

    df_melted = df_melted.dropna()
    df_melted.reset_index(drop=True,inplace=True)
    return df_melted

#USANDO REGEX EXTRAEMOS EL NOMBRE DE CADA PRODUCTO
def procesar_dataframe_con_producto(x):
    def obtener_producto(z):
        match_producto = re.search(r'name:(.*?)(?=\|)', z)
        if match_producto:
            valor_producto = str(match_producto.group(1))
            return valor_producto
        else:
            return None

    x['producto'] = x['value'].apply(obtener_producto)
    return x

#EXTRAEMOS LA CANTIDAD COMPRADA DE CADA PRODUCTO
def procesar_dataframe_con_cantidad(x):
    def obtener_cantidad(z):
        match_cantidad = re.search(r'quantity:(\d+\.?\d*)', z)
        if match_cantidad:
            valor_cantidad = int(match_cantidad.group(1))
            return valor_cantidad
        else:
            return None

    x["quantity"] = x["value"].apply(obtener_cantidad)
    return x

#EXTRAEMOS EL PRECIO TOTAL DE CADA PRODUCTO
def procesar_dataframe_con_total_precio(x):
    def obtener_total_precio(z):
        match_total = re.search(r'total:(\d+\.?\d*)', z)
        if match_total:
            valor_total = float(match_total.group(1))
            return valor_total
        else:
            return None

    x['total_precio'] = x['value'].apply(obtener_total_precio)
    return x

#UNIMOS NOMBRE Y APELLIDOS DE CADA CLIENTE EN UNA MISMA COLUMNA. TIRAMOS LAS COLUMNAS QUE YA NO VAMOS A USAR
#PORQUE LAS HEMOS REEMPLAZADO EN LAS FUNCIONES ANTERIORES. CAMBIAMOS EL NOMBRE DE LAS COLUMNAS.
def procesar_dataframe(x):
    x['nombre_completo'] = x['billing_first_name'] + ' ' + x['billing_last_name']
    x.drop(["billing_first_name", "billing_last_name", "value", "line_item"], axis=1, inplace=True)

    columnas_dic = {
        'order_date': 'fecha',
        'order_number': 'id_order',
        'status': 'status',
        'nombre_completo': 'Cliente',
        'producto': 'product_name',
        'quantity': 'product_quantity',
        'total_precio': 'total_price_tax_incl'
    }

    x.rename(columns=columnas_dic, inplace=True)

    return x

#FUNCION PARA LIMPIAR LAS STRINGS DE TILDES Y DE MAYUSCULAS
def clean(x):
    x = x.lower()
    x = re.sub(r'\W', ' ', x)
    x=unidecode(x)
    return x

#FUNCION PARA SACAR DE CADA PRODUCTO EL TIPO DE PESCADO Y ADEMAS ASIGNARLE UN NUMERO PARA PASAR ESTA VARIABLE A NUMERICA
def asignar_pescado_y_numero(x):
    pescados_espanol = ["atun", "melva", "caballa", "jurel", "sardina", "boquerones", "anchoas", "sardinillas",
                        "surtido", "huevas de maruca", "huevas de bacalao", "ventresca", "calamares", "mojama", "mejillones",
                        "berberechos", "salmon", "hueva de maruca", "huevas bacalao", "boqueron", "bacalao", "anchoa", "caballitas",
                        "bonito", "gambas", "sal"]

    pescados_ingles = ["tuna", "mackerel", "mackerel", "mackerel", "sardine", "anchovies", "anchovies", "small sardines",
                       "assorted", "mullet roe", "cod roe", "ventresca", "squid", "mojama", "mussels",
                       "cockles", "salmon", "mullet roe", "cod roe", "anchovy", "cod", "anchovy", "baby horse mackerels",
                       "bonito", "shrimp", "salt"]

    lista_listas = [list(z) for z in zip(pescados_espanol, pescados_ingles)]

    def asignar_pescado(row):
        for i, pescado in enumerate(lista_listas):
            for elemento in pescado:
                if elemento in row:
                    return pescado[0]
        return None

    def asignar_numero(row):
        for i, pescado in enumerate(lista_listas):
            for elemento in pescado:
                if elemento in row:
                    return i
        return None

    x["pescado"] = x["product_minuscula"].apply(asignar_pescado)
    x["numero_pescado"] = x["product_minuscula"].apply(asignar_numero)

    return x

#ASIGNAR MARCA Y SU EQUIVALENTE NUMERICO(AL TRANSFORMAR A VARIABLE NUMERICA)
def asignar_marca_y_num_marca(x):
    lista_marcas = ["usisa", "tejero", "decano"]

    def asignar_marca(row):
        for i, marca in enumerate(lista_marcas):
            if marca in row:
                return marca
        return "usisa"

    def asignar_num_marca(row):
        for i, marca in enumerate(lista_marcas):
            if marca in row:
                return i
        return 0

    x["marca"] = x["product_minuscula"].apply(asignar_marca)
    x["marca_id"] = x["product_minuscula"].apply(asignar_num_marca)

    return x

#ASIGNAR EL TIPO DE ACEITE Y SU VARIABLE NUMERICA CORRESPONDIENTE
def asignar_aceite_y_numero(x):
    lista_aceite_esp = ["girasol", "oliva", "virgen", "escabeche", "tomate"]
    lista_aceite_eng = ["sunflower", "olive", "virgin", "escabeche", "tomato"]
    eng_esp_aceite = [list(z) for z in zip(lista_aceite_esp, lista_aceite_eng)]

    def asignar_aceite(row):
        for aceite in eng_esp_aceite:
            for elemento in aceite:
                if elemento in row:
                    return aceite[0]
        return "otros"

    def asignar_aceite_num(row):
        for i, aceite in enumerate(eng_esp_aceite):
            for elemento in aceite:
                if elemento in row:
                    return i
        return 5

    x["aceite"] = x["product_minuscula"].apply(asignar_aceite)
    x["numero_aceite"] = x["product_minuscula"].apply(asignar_aceite_num)

    return x

#EXTRAER EL PESO DE CADA PRODUCTO Y RELLENAR LOS VALORES NULOS. LA MEDIA ERA APROX. 400. HEMOS DECIDIDO RELLENARLOS CON ALGO MENOS: 299.
def sacar_pesos_especificos(cadena):
    lista_pesos = ["1", "5", "70", "80", "88", "90", "100", "120", "125", "130", "125", "150", "190", "200", "210",
                   "230", "240", "250", "300", "350", "500", "750", "1000"]

    patron_peso = re.compile(r'(\d+(?:\s*x\s*\d+)?)\s*(?:gr|kg|ro|rr)')
    coincidencias = patron_peso.findall(cadena)
    pesos = [valor.replace(" ", "") for valor in coincidencias if valor]
    pesos_validos = [p for p in pesos if p in lista_pesos]

    resultado = pesos_validos[0] if pesos_validos else None
    if resultado in ["1", "5", "3"]:
        resultado = str(int(resultado) * 1000)

    return resultado
#USA LA FUNCION ANTERIOR DE PESO Y COMO SE HA COMENTADO ANTES REEMPLAZA NULLS POR 299.
def procesar_pesos(x):
    x["peso"] = x["product_minuscula"].apply(sacar_pesos_especificos)
    x["peso"].fillna(299, inplace=True)
    x["peso"] = x["peso"].astype(int)
    return x

#*********************************



# # FUNCIONES PARA DF ANTIGUO (HISTORICO: MEZCLA DE ANTIGUO Y NUEVO)



#CREAMOS COLUMNA STATUS Y ASIGNANDOLOS COMPLETADOS. CAMBIAMOS EL FORMATO DEL PRECIO.
def procesar_df_antiguo(x):
    #x.drop("Referencia del pedido ", axis=1, inplace=True)
    x["status"]="Completed"
    x["total_price_tax_incl"]=x["total_price_tax_incl"]/1000000
    return x



#CONCATENAMOS EL DATAFRAME ANTIGUO CON EL NUEVO. MANTENEMOS LAS COLUMNAS DESEADAS EN EL ORDEN DESEADO.
def concatenar(x_antiguo,x_nuevo):
    df=pd.concat([x_nuevo,x_antiguo], axis=0)
    df.reset_index(drop=True, inplace=True)
    column_order = ["id_order", "Cliente", "fecha", "product_name", "product_quantity", "total_price_tax_incl", "status"]
    df=df[column_order]
    return df

#FUNCION PARA LIMPIAR LAS STRINGS DE TILDES Y DE MAYUSCULAS
def clean(x):
    x = x.lower()
    x = re.sub(r'\W', ' ', x)
    x=unidecode(x)
    return x


#MISMA FUNCION QUE LA ANTERIOR PARA EXTRAER EL TIPO DE PESCADO Y SU EQUIVALENTE NUMERICO. ESTÁ ESCRITA DOBLEMENTE POR CUESTION DE ESTRUCTURA PARA TENERLO EN CUENTA NOSOTROS
def asignar_pescado_y_numero(x):
    pescados_espanol = ["atun", "melva", "caballa", "jurel", "sardina", "boquerones", "anchoas", "sardinillas",
                        "surtido", "huevas de maruca", "huevas de bacalao", "ventresca", "calamares", "mojama", "mejillones",
                        "berberechos", "salmon", "hueva de maruca", "huevas bacalao", "boqueron", "bacalao", "anchoa", "caballitas",
                        "bonito", "gambas", "sal"]

    pescados_ingles = ["tuna", "mackerel", "mackerel", "mackerel", "sardine", "anchovies", "anchovies", "small sardines",
                       "assorted", "mullet roe", "cod roe", "ventresca", "squid", "mojama", "mussels",
                       "cockles", "salmon", "mullet roe", "cod roe", "anchovy", "cod", "anchovy", "baby horse mackerels",
                       "bonito", "shrimp", "salt"]

    lista_listas = [list(z) for z in zip(pescados_espanol, pescados_ingles)]

    def asignar_pescado(row):
        for i, pescado in enumerate(lista_listas):
            for elemento in pescado:
                if elemento in row:
                    return pescado[0]
        return None

    def asignar_numero(row):
        for i, pescado in enumerate(lista_listas):
            for elemento in pescado:
                if elemento in row:
                    return i
        return None

    x["pescado"] = x["product_minuscula"].apply(asignar_pescado)
    x["numero_pescado"] = x["product_minuscula"].apply(asignar_numero)

    return x


#MISMA FUNCION PARA EXTRAER MARCA Y EQUIVALENTE NUMERICO
def asignar_marca_y_num_marca(x):
    lista_marcas = ["usisa", "tejero", "decano"]

    def asignar_marca(row):
        for i, marca in enumerate(lista_marcas):
            if marca in row:
                return marca
        return "usisa"

    def asignar_num_marca(row):
        for i, marca in enumerate(lista_marcas):
            if marca in row:
                return i
        return 0

    x["marca"] = x["product_minuscula"].apply(asignar_marca)
    x["marca_id"] = x["product_minuscula"].apply(asignar_num_marca)

    return x



#MISMA FUNCION PARA EXTRAER ACEITE Y EQUIVALENTE NUMERICO
def asignar_aceite_y_numero(x):
    lista_aceite_esp = ["girasol", "oliva", "virgen", "escabeche", "tomate"]
    lista_aceite_eng = ["sunflower", "olive", "virgin", "escabeche", "tomato"]
    eng_esp_aceite = [list(z) for z in zip(lista_aceite_esp, lista_aceite_eng)]

    def asignar_aceite(row):
        for aceite in eng_esp_aceite:
            for elemento in aceite:
                if elemento in row:
                    return aceite[0]
        return "otros"

    def asignar_aceite_num(row):
        for i, aceite in enumerate(eng_esp_aceite):
            for elemento in aceite:
                if elemento in row:
                    return i
        return 5

    x["aceite"] = x["product_minuscula"].apply(asignar_aceite)
    x["numero_aceite"] = x["product_minuscula"].apply(asignar_aceite_num)

    return x


#FUNCION PARA EXTRAER LOS PESOS ANTERIORMENTE MENCIONADA
def sacar_pesos_especificos(cadena):
    lista_pesos = ["1", "5", "70", "80", "88", "90", "100", "120", "125", "130", "125", "150", "190", "200", "210",
                   "230", "240", "250", "300", "350", "500", "750", "1000"]

    patron_peso = re.compile(r'(\d+(?:\s*x\s*\d+)?)\s*(?:gr|kg|ro|rr)')
    coincidencias = patron_peso.findall(cadena)
    pesos = [valor.replace(" ", "") for valor in coincidencias if valor]
    pesos_validos = [p for p in pesos if p in lista_pesos]

    resultado = pesos_validos[0] if pesos_validos else None
    if resultado in ["1", "5", "3"]:
        resultado = str(int(resultado) * 1000)

    return resultado
#FUNCION PROCESAR PESOS QUE USA LA FUNCION ANTERIOR DE PESOS ESPECIFICOS. AMBAS EXPLICADAS ANTERIORMENTE.
def procesar_pesos(x):
    x["peso"] = x["product_minuscula"].apply(sacar_pesos_especificos)
    x["peso"].fillna(299, inplace=True)
    x["peso"] = x["peso"].astype(int)
    return x

#MANTENER SOLO LAS ORDENES COMPLETADAS Y DESHACERNOS DEL INDICE
def limpiar_status(x):
    x["status"]=x["status"].apply(clean)
    x=x.loc[x["status"]=="completed"]
    x.reset_index(drop=True, inplace=True)
    return x


#FUNCION PARA LIMPIAR DE MAYUSCULAS, TILDES, NOMBRES DE PRUEBA LA COLUMNA CLIENTE
def limpiar_cliente(x):
    x["Cliente"]=x["Cliente"].apply(clean)
    x=x[x["Cliente"]!="no nonono"]
    x['cliente_id_unica'] = pd.factorize(x['Cliente'])[0]
    x.reset_index(drop=True, inplace=True)
    return x



#FUNCION PARA ELIMINAR LOS PEDIDOS DE PRUEBA
def eliminar_pruebas(x):
    df = x.drop(x[x["product_minuscula"] == 'anulfra'].index)
    productos_a_eliminar = ['producto prueba', 'producto de prueba', 'prueba']
    df.drop(df[df["product_minuscula"].isin(productos_a_eliminar)].index, inplace=True)
    id_orders_a_eliminar = [i for i in range(1,6)]
    df.drop(df[df["id_order"].isin(id_orders_a_eliminar)].index, inplace=True)
    return df



#FUNCION PARA RENOMBRAR COLUMNAS A ESPAÑOL CON UN FORMATO MAS UNIFICADO
def renombrar(x):
    diccionario_columnas={'id_order':"id_pedido",
                          'Cliente': "nombre_cliente",
                          'product_name': "nombre_producto",
                          'product_quantity': "cantidad_producto",
                          'total_price_tax_incl': "precio_total", 
                          'status': "estado",
                          'product_minuscula': "nombre_producto_minuscula",
                          'numero_pescado': "id_pescado",
                          'marca_id': "id_marca",
                          'numero_aceite': "id_aceite"}
    x_renombrado=x.rename(columns=diccionario_columnas)
    return x_renombrado


# # FUNCIONES FINALES CON LAS DEMAS FUNCIONES DENTRO

#FUNCION GLOBAL PARA DF NUEVO
def todas_las_funciones_nuevo_postal(x):
    
    x=tirar_columnas_nuevo_email_postal(x)
    x=desglosar_items(x)
    x=procesar_dataframe_con_producto(x)
    x=procesar_dataframe_con_cantidad(x)
    x=procesar_dataframe_con_total_precio(x)
    x=procesar_dataframe(x)
    x["product_minuscula"]=x["product_name"].apply(clean)
    x=asignar_pescado_y_numero(x)
    x=asignar_marca_y_num_marca(x)
    x=asignar_aceite_y_numero(x)
    x=procesar_pesos(x)
    return x



#FUNCION GLOBAL PARA DF HISTORICO(ANTIGUO+NUEVO)

def todas_las_funciones_historico(antiguo,nuevo):
    nuevo.drop(['billing_postcode', 'billing_city', 'billing_email'], axis=1, inplace=True)
    antiguo=procesar_df_antiguo(antiguo)
    x=concatenar(antiguo,nuevo)
    x["product_minuscula"]=x["product_name"].apply(clean)
    x=asignar_pescado_y_numero(x)
    x=asignar_marca_y_num_marca(x)
    x=asignar_aceite_y_numero(x)
    x=procesar_pesos(x)
    x=limpiar_status(x)
    x=limpiar_cliente(x)
    x=eliminar_pruebas(x)
    x=renombrar(x)
    return x


#HEATMAP PARA VISUALIZACION


def heatmap_triu(X):
    matrix=X.corr()
    mask=np.zeros_like(matrix)
    mask[np.triu_indices_from(mask)]=True
    
    sns.heatmap(matrix,
            center=0,
            fmt=".3f",
            mask=mask,
            square=True, linewidth=0.3,
            annot=True, cmap='coolwarm')

    plt.show()


#TRANSFORMACION TIMESERIES
#AGRUPAR PEDIDOS Y PRECIOS MENSUALMENTE
def transformar_timeseries_mensual(x):

    x["fecha"]=pd.to_datetime(x["fecha"])

    df_agrupado_mensual = x.groupby(x['fecha'].dt.to_period("M")).agg({
        'id_pedido': 'nunique',
        'precio_total': 'sum'
    }).reset_index()


    df_agrupado_mensual.columns = ['Mes', 'Total_Pedidos_mes', 'Total_Precios_mes']
    df_agrupado_mensual['Mes'] = df_agrupado_mensual['Mes'].astype(str)
    return df_agrupado_mensual

#AGRUPAR PEDIDOS Y PRECIOS SEMANALMENTE
def transformar_timeseries_semanal(x):

    x["fecha"]=pd.to_datetime(x["fecha"])

    df_agrupado_mensual = x.groupby(x['fecha'].dt.to_period("W")).agg({
        'id_pedido': 'nunique',
        'precio_total': 'sum'
    }).reset_index()


    df_agrupado_mensual.columns = ['Semana', 'Total_Pedidos_semana', 'Total_Precios_semana']
    df_agrupado_mensual['Semana'] = df_agrupado_mensual['Semana'].astype(str)
    return df_agrupado_mensual




#FUNCION GLOBAL PARA DF NUEVO PARA MODELO CLUSTER
#EXTRAEMOS EN UN DATAFRAME LA FRECUENCIA, LO RECIENTE, TOTAL PAGADO, CUANTOS PEDIDOS... POR CLIENTE UNICO CON SU CORRESPONDIENTE ID UNICA
def frecuencia_nuevo(df_nuevo_cliente):
    result_df = df_nuevo_cliente.copy()

    result_df["fecha"] = pd.to_datetime(result_df["fecha"])

    max_date_per_client = result_df.groupby("Cliente")["fecha"].max().reset_index()

    result_df = result_df.merge(max_date_per_client, on="Cliente", suffixes=('', '_max'))

    day = pd.to_datetime(result_df["fecha_max"].max())
    result_df['ultima_compra'] = result_df.groupby('Cliente')['fecha'].transform(lambda x: (day - x.max()).days)

    result_df['conteo'] = result_df.groupby('Cliente')['id_order'].transform('nunique')

    total_purchases = result_df['conteo'].sum()
    result_df['frecuencia'] = result_df['conteo'] / total_purchases

    result_df['cliente_id_unica'] = result_df['Cliente'].astype('category').cat.codes

    result_df['precio_total_cliente'] = result_df.groupby('Cliente')['precio_total'].transform('sum')
    
    result_df['codigo_postal'] = result_df.groupby('Cliente')['billing_postcode'].transform('max')
    result_df['ciudad'] = result_df.groupby('Cliente')['billing_city'].transform('max')
    result_df['email'] = result_df.groupby('Cliente')['billing_email'].transform('max')

    result_df = result_df[['cliente_id_unica', 'ultima_compra', 'conteo', 'frecuencia', 'Cliente',
                           'precio_total_cliente', 'codigo_postal', 'ciudad', 'email']]

    result_df = result_df.drop_duplicates(subset=['cliente_id_unica'])

    return result_df






