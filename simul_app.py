import streamlit as st
import pandas as pd
import numpy as np
import altair as alt

st.write("""# ¿Que me conviene? ¿Arrendar o comprar?: Un ejercicio simulado.

## Escenario

Supongamos que encontramos el departamento de nuestros sueños el cuál tienen una carácteristica especial. 
Podemos elegir entre comprarlo o arrendarlo. Dónde el precio de venta es de 2000UF y arrendarlo 8 UF mensuales. 

### Gastos
Ahora si tuviesemos los 2000UF podríamos comprarlo de inmediato. Pero lamentablemente no es así.
Sólo disponemos de 400UF, que ahorramos anteriormente, pero el resto tendrá que ser financiado vía crédito. 

Naturalmente, el banco no nos prestará gratis los 1600 UF restantes. Para eso nos ofrece un 
crédito tiene con una tasa de interés de 3% fija a pagar mensualmente a pagar durante 20 años. Esto, en terminos de dividendo 
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
tasa_interes = st.sidebar.slider(min_value=1.0,max_value= 10.0, step= 0.05,value = 1.5, label="Interés",format="%g%%")/100

rentabilidad_ffmm = st.sidebar.slider(min_value=1.0,max_value= 10.0, step= 0.05,value = 1.5,
label="Rentabilidad FFMM", format="%g%%")/100/12

plazo_meses = plazo*12

periodic_tasa_interes = (1+tasa_interes)**(1/12) - 1
dividendo = -1*np.pmt(periodic_tasa_interes , plazo_meses, costo_propiedad - pie)

costo_arriendo = st.sidebar.slider(min_value=6,max_value= 50, step =2, value = 8,label="Costo Arriendo", format="%g UF")

if dividendo - costo_arriendo <=0:
    ahorro_mensual = 0
else:
    ahorro_mensual = dividendo - costo_arriendo

ahorro_mensual = round(ahorro_mensual, 2)

st.sidebar.write(f'Pie Inicial/Capital Inicial FFMM: {round(pie, 2)} UF')
st.sidebar.write(f'Ahorro mensual de arriendo: {ahorro_mensual} UF')


def gen_data(costo_propiedad, pie, plazo_meses, tasa_interes, rentabilidad_ffmm, costo_arriendo):

    credito_remanente = np.zeros(plazo_meses)
    interes_cuota_arr = np.zeros(plazo_meses)
    amortizacion_cuota_arr = np.zeros(plazo_meses)
    capital_ffmm = np.zeros(plazo_meses)
    credito_solicitado = costo_propiedad - pie
    periodic_tasa_interes = (1+tasa_interes)**(1/12) - 1
    dividendo = -1*np.pmt(periodic_tasa_interes , plazo_meses, credito_solicitado)
    #costo_total = dividendo * plazo_meses
    if dividendo - costo_arriendo <=0:
        ahorro_mensual = 0
    else:
        ahorro_mensual = dividendo - costo_arriendo

    for i in range(0, plazo_meses):
        ## Compra
        if i == 0:
            previous_credito_remanente = credito_solicitado
            previous_capital_ffmm = pie
        else:
            previous_credito_remanente = credito_remanente[i-1]
            previous_capital_ffmm = capital_ffmm[i-1]
            
        interes_cuota = round(previous_credito_remanente*periodic_tasa_interes, 2)
        amortizacion_cuota = round(dividendo - interes_cuota, 2)
    
        if previous_credito_remanente - amortizacion_cuota < 0:
            amortizacion_cuota = previous_credito_remanente
        
        interes_cuota_arr[i] = interes_cuota 
        amortizacion_cuota_arr[i] = amortizacion_cuota
        credito_remanente[i] = previous_credito_remanente - amortizacion_cuota

        capital_ffmm[i]= (previous_capital_ffmm+ahorro_mensual)*(1+ rentabilidad_ffmm)
    

    mes_num = np.arange(plazo_meses)
    mes_num = mes_num + 1

    credito_remanente = np.around(credito_remanente, decimals=2)

    list_valorzcn = [1]

    for i in range(plazo_meses-1):
        list_valorzcn.append(list_valorzcn[i]*1 + tasa_interes/12) 

    new_gasto = (costo_propiedad - credito_remanente)
    new_gasto = new_gasto *list_valorzcn
    
    pymnts_df = pd.DataFrame({'Mes':mes_num,  'Capital valorizado':new_gasto , 
    'Gasto total realizado': pie + (dividendo * mes_num), 'Amortización':  amortizacion_cuota_arr, 
    'Interés($)':interes_cuota_arr})


    ffmm_df = pd.DataFrame({'Mes':mes_num,  'Costo Arriendo':costo_arriendo, 'Capital FFMM': capital_ffmm,
    '0_aux': [0]*plazo_meses})

    return pymnts_df, ffmm_df

pymnts_df, ffmm_df = gen_data(costo_propiedad, pie, plazo_meses, tasa_interes, rentabilidad_ffmm, costo_arriendo)


st.table(pymnts_df[:11], )

st.table(ffmm_df[:11], )


def gen_compra_chart(pymnts_df):
    tri_range = ['red', 'blue', 'green']
    tri_domain = ['Capital valorizado', 'Gasto total realizado', "Rentabilidad"]

    base = alt.Chart(data = pymnts_df)
    c = base.transform_fold(
    fold=['Capital valorizado', 'Gasto total realizado'],
    as_=['Tipo', 'UF']
    ).mark_line().encode(
    x = 'Mes:Q',
    y = 'UF:Q',
    color=alt.Color('Tipo:N', scale=alt.Scale(range=tri_range, 
    domain=tri_domain), legend=alt.Legend(title=None))
    )

    vlines = base.transform_calculate(
    name='"Rentabilidad"'  
    ).mark_rule(opacity=0.9).encode(
        x='Mes:Q',x2='Mes:Q',
        y='Capital valorizado:Q',
        y2='Gasto total realizado:Q',
    color=alt.Color('name:N', scale=alt.Scale(range=tri_range, 
        domain=tri_domain), legend=alt.Legend(title=None))
    )
    c =c + vlines
    c.layer[0].encoding.y.title = 'UF'
    return c

def gen_arrdo_chart(ffmm_df):
    base = alt.Chart(data = ffmm_df)
    bi_range = ['red',  'green']
    bi_domain = ['Capital FFMM', "Rentabilidad"]

    c2 = base.transform_fold(
        fold=['Capital FFMM'],
        as_=['Tipo', 'UF']
    ).mark_line().encode(
        x = 'Mes:Q',
        y = 'UF:Q',
        color=alt.Color('Tipo:N', scale=alt.Scale(range=bi_range, 
        domain=bi_domain), legend=alt.Legend(title=None))
    )


    vlines2 = base.transform_calculate(
        name='"Rentabilidad"'  
    ).mark_rule(opacity=0.9).encode(
        x='Mes:Q',x2='Mes:Q',
        y='Capital FFMM:Q',y2='0_aux:Q',
    color=alt.Color('name:N', scale=alt.Scale(range=bi_range, 
        domain=bi_domain), legend=alt.Legend(title=None))
    )

    c2= c2 + vlines2
    c2.layer[0].encoding.y.title = 'UF'

    return c2

st.write("""## Rentabilidad de comprar: 

Veamoslo de forma gráfica con los parámetros que establecimos.

* La linea azul representa el monto de la propiedad de la cual somos dueños también el aúmento de su valorización.
* La línea verde lo que hemos pagado del crédito de forma acumulada hasta el mes respectivo.
* Finalmente, la línea negra es la diferencia entre la linea azul y verde y por consiguiente la rentabilidad neta por mes.
""")

#st.altair_chart(gen_compra_chart(pymnts_df), use_container_width=True)

cmpd = gen_compra_chart(pymnts_df) |gen_arrdo_chart(ffmm_df)
st.write("""## Rentabilidad de Arrendar: 

* 
* 
* 
""")

st.altair_chart(cmpd, use_container_width=True)



#############################################################################################
costo_propiedad = 2000
pie = 400
# credito_solicitado = 1600
plazo_meses = 20*12
tasa_interes = 4 / 100
periodic_tasa_interes = (1+tasa_interes)**(1/12) - 1
#dividendo = -1*np.pmt(periodic_tasa_interes , plazo_meses, credito_solicitado)

#costo_total = dividendo * 240
rentabilidad_ffmm = 0.05/12


pymnts_df, ffmm_df = gen_data(costo_propiedad, pie, plazo_meses, tasa_interes, rentabilidad_ffmm, costo_arriendo)

"""La rentabilidad es entonces

"""

st.table(pymnts_df[:11], )

st.altair_chart(gen_compra_chart(pymnts_df), use_container_width=True)
st.altair_chart(gen_arrdo_chart(ffmm_df), use_container_width=True)


