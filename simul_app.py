from numpy.lib import financial
import streamlit as st
import pandas as pd
import numpy as np
import numpy_financial as npf
import altair as alt
from altair import datum


st.write("""# ¿Que me conviene, arrendar o comprar?: Un ejercicio simulado.

## Introducción

La respuesta es obvia dirán algunos... Si puedes, conviene siempre comprar!!! Pero esto es claramente incorrecto, dado a que tenemos
2 alternativas financieras que compiten. Principalmente, cómo precio de venta, tasa de interés, plazo de crédito o valorización esperada
por un lado o precio de arriendo, rentabilidad esperada de alternativa de inversión por otro lado.
Ciertamente, es que encontraremos una combinación en donde arrendar sea más financieramente conveniente que comprar. 
Pero cuál es ese punto. Al parecer, entonces, la pregunta parece estar mal formulado, más bien. ¿Cuando conviene, o en que condiciones comprar vs arrendar?
El presente articúlo es un ejercicio simulado que intenta descubrir ese punto de inflexión.

## Escenario 

Supongamos que encontramos el departamento de nuestros sueños el cuál tienen una carácteristica especial. 
Podemos elegir entre comprarlo o arrendarlo. Dónde el precio de venta es de 2000UF y arrendarlo 8 UF mensuales. 

### Gastos
Ahora si tuviesemos los 2000UF podríamos comprarlo de inmediato. Pero lamentablemente no es así.
Sólo disponemos de 400UF, que ahorramos anteriormente, pero el resto tendrá que ser financiado vía crédito. 

Naturalmente, el banco no nos prestará gratis los 1600 UF restantes. Para eso nos ofrece un 
crédito tiene con una tasa de interés de 3% fija a pagar mensualmente durante 20 años. Esto, en terminos de dividendo 
se traduce en 8.84 UF mensuales (más detalles de este cálculo en otro post). Supongamos también que el único costo complementario asociado corresponden a las contribuciones. 
Items cómo seguros, costos notariales y cómisiones son 0. Los gastos comunes tampoco en este caso debemos considerarlo 
en el ánalisis, dado que es un costo que debe asumir quien ocupe el departamento, ya sea propietario o arrendatario.

### Valorización
Ahora bien, eso son los parametros que definimos para cuantificar el costo del departamento, pero nos queda la otra 
dimensión clave de nuestro análisis que es la valorización que puede tener la propiedad o del capital que logremos ahorrar
al ser el gasto por arriendo menor a los dividendos. 
En efecto, muchos invirtien en un bien raíz, justamente, por la esperanza que este se valorice en el tiempo. Quizás muchos han escuchado el dicho,
'Propiedades, siempre para arriba, autos, siempre para abajo'. De igual forma, otros dirán que la propiedades no es lo único que se valoriza,
también lo hacen instrumentos financieros como depositos a plazo, acciones o fondos mutuos. Donde la promesa, es qué, gracias al interés compuesto, 
después de unos cuantos años nuestra inversión inicial crezca. Ambas son alternativas válidas y que tenemos que considerar en nuestro análisis.

Para llevar esto a números, supongamos entonces que la propiedad se valoriza a una tasa de 4% anual, mientras que la rentabilidad de nuestro fondo 
es de 5% anual. 


### Resumen (hasta ahora)

El dilema que entonces nos queda es el siguiente, que es más conveniente o rentable, pagar el crédito para comprar el departamento
y al cabo de 20 años que un bien de 2000 UF sea enteramente nuestro, o arrendar, para poder aumentando nuestra capacidad de ahorro, 
invirtiendo a su vez en un fondo mutuo, quizás, el cuál pueda rentabilizarse durante el transcurso. Para ello miremos los números
que se muestran en el siguiente cuadro resumen para luego simular nuestras dos alternativas de inversión por separado""")

df_res = pd.DataFrame({'Ítem': ['Pie Inicial/Capital Inicial FFMM','Dividendo/Arriendo Mensual', 'Valorización/Rentabilidad', 'Plazo'], 
'Compra': ["400 UF", "8.84 UF", "4%", '20 años'], 'Arriendo': ["400", "8 UF", "5%", '20 años']})

st.table(df_res)


## Compra params

costo_propiedad = st.sidebar.slider(min_value=1000,max_value= 15000, step =100, value = 2000,label="Costo Propiedad", format="%g UF")

pie = st.sidebar.slider(min_value=10, max_value= 100, step = 5, 
value = 20, label="Pie Inicial/Capital Inicial FFMM", format="%g%%")*costo_propiedad/100


plazo = st.sidebar.slider(min_value=10,max_value= 30, step= 5, value = 20, format="%g años", label="Plazo")
tasa_interes = st.sidebar.slider(min_value=1.0,max_value= 10.0, step= 0.05,value = 1.5, label="Tasa Interés anual",format="%g%%")/100
plusvalia = st.sidebar.slider(min_value=1.0,max_value= 10.0, step= 0.05,value = 1.5, label="Plusvalía anual",format="%g%%")/100


rentabilidad_ffmm = st.sidebar.slider(min_value=1.0,max_value= 10.0, step= 0.05,value = 1.5,label="Rentabilidad FFMM", format="%g%%")/100

plazo_meses = plazo*12

periodic_tasa_interes = (1+tasa_interes)**(1/12) - 1
dividendo = -1*npf.pmt(periodic_tasa_interes , plazo_meses, costo_propiedad - pie)
dividendo =round(1.2*dividendo, 2)

costo_arriendo = st.sidebar.slider(min_value=3.0, max_value= round(1.2*dividendo, 2), step =.5, label="Costo Arriendo", format="%g UF")

ahorro_mensual = dividendo - costo_arriendo

ahorro_mensual = round(ahorro_mensual, 2)


st.sidebar.write(f'Pie/Capital Inicial FFMM: {int(pie)} UF')
st.sidebar.write(f'Dividendo: {dividendo} UF')
st.sidebar.write(f'Ahorro mensual de arriendo: {ahorro_mensual} UF')


def gen_data(costo_propiedad, pie, plazo_meses, tasa_interes, rentabilidad_ffmm, costo_arriendo, plusvalia):
        
    mes_num = np.arange(plazo_meses)
    mes_num = mes_num + 1

    amortizacion_cuota_arr = npf.ppmt(tasa_interes/12, mes_num, plazo_meses, pv = -(costo_propiedad-pie))
    capital_adeudado = costo_propiedad-pie-np.cumsum(amortizacion_cuota_arr)

    interes_cuota_arr = npf.ipmt(tasa_interes/12, mes_num, plazo_meses, pv = -(costo_propiedad-pie))

    dividendos = interes_cuota_arr + amortizacion_cuota_arr

    total_pagado_credito = pie + np.cumsum(dividendos)

    ahorro_mensual = dividendos - costo_arriendo

    costo_prepago = capital_adeudado + 1.5*interes_cuota_arr
    
    capital_ffmm = npf.fv(rentabilidad_ffmm/12, mes_num, pv = -pie, pmt =-ahorro_mensual)
    list_valorzcn =npf.fv(plusvalia/12, mes_num, pv = -costo_propiedad, pmt =0)

    rentabilidad_br = (list_valorzcn - costo_prepago)
    
    df = pd.DataFrame({'Mes':mes_num,  'Propiedad valorizada':list_valorzcn, 
    'Gasto crédito acumulado': total_pagado_credito, 'Amortización':  amortizacion_cuota_arr, 
    'Interés($)':interes_cuota_arr, 'Costo Arriendo':costo_arriendo, 'Capital FFMM': capital_ffmm, 
    'Rentabilidad': rentabilidad_br, "Capital adeudado": capital_adeudado, 'Costo prepago': costo_prepago})

    return df

df = gen_data(costo_propiedad, pie, plazo_meses, tasa_interes, rentabilidad_ffmm, costo_arriendo, plusvalia)


def gen_chart(df):
    range = ['red', 'blue', 'green', 'purple']
    domain = ['Propiedad valorizada', 'Costo prepago', "Rentabilidad", 'Capital FFMM']

    base = alt.Chart(data = df).transform_fold(
        fold=['Propiedad valorizada', 'Costo prepago', 'Capital FFMM', 'Rentabilidad'],
        as_=['Tipo', 'UF']
        ).transform_calculate(
            name='"Rentabilidad"'  
        )

    c = base.transform_filter(
        alt.FieldOneOfPredicate(field='Tipo', oneOf=['Propiedad valorizada', 'Costo prepago', 'Capital FFMM'])
    ).mark_line().encode(
    x = 'Mes:Q',
    y = 'UF:Q',
    color=alt.Color('Tipo:N', scale=alt.Scale(range=range, 
    domain=domain), legend=alt.Legend(title=None))
    )

    area = base.mark_area(opacity=0.9).encode(
        x='Mes:Q',x2='Mes:Q',
        y='Propiedad valorizada:Q',
        y2='Costo prepago:Q',
    color=alt.Color('name:N', scale=alt.Scale(range=range, 
        domain=domain), legend=alt.Legend(title=None))
    )
    c =c + area

    c.layer[0].encoding.y.title = 'UF'

    res = base.transform_filter(
        alt.FieldOneOfPredicate(field='Tipo', oneOf=['Capital FFMM', 'Rentabilidad'])
    ).mark_line().encode(
    x = 'Mes:Q',
    y = 'UF:Q',
    color=alt.Color('Tipo:N', scale=alt.Scale(range=range, 
    domain=domain), legend=alt.Legend(title=None))
    )

    return alt.vconcat(c, res)


st.write("""## Rentabilidad de comprar: 

Veamoslo de forma gráfica con los parámetros que establecimos.

* La linea azul representa el monto de la propiedad de la cual somos dueños también el aúmento de su valorización.
* La línea verde lo que hemos pagado del crédito de forma acumulada hasta el mes respectivo.
* Finalmente, la línea negra es la diferencia entre la linea azul y verde y por consiguiente la rentabilidad neta por mes.
""")

#st.altair_chart(gen_compra_chart(pymnts_df), use_container_width=True)

cmpd = gen_chart(df)
st.write("""## Rentabilidad de Arrendar: 

* 
* 
* 
""")

st.altair_chart(cmpd, use_container_width=True)



#############################################################################################
costo_propiedad = 2000
pie = 400
plazo_meses = 20*12
tasa_interes = 4 / 100
periodic_tasa_interes = (1+tasa_interes)**(1/12) - 1
plusvalia = 0.05

rentabilidad_ffmm = 0.05/12


#df = gen_data(costo_propiedad, pie, plazo_meses, tasa_interes, rentabilidad_ffmm, costo_arriendo, plusvalia)

"""La rentabilidad es entonces

"""

#st.altair_chart(gen_chart(df), use_container_width=True)


