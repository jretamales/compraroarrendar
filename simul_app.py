import streamlit as st
import pandas as pd
import numpy as np
import numpy_financial as npf
import altair as alt

st.write("""# ¿Cuándo conviene arrendar ? Un ejercicio simulado.

## Introducción

La respuesta es obvia dirán algunos... Si te alcanza para el pie, nunca conviene arrendar, siempre comprar!!! 
Pero esto es claramente incorrecto. Debe existir una combinación de precio de venta, arriendo, tasa de interés, etc., 
por más insólita que parezca, que haga más conveniente el arriendo. Pero cómo encontrar, esa combinación cuando las variables
son múltiples y con formulas que para mucha gente resulta desconocida o demasiado complicada. 
Para resolver esta dificultad, es que generé esta simulación que permite interactuar con las variables 
que determinan cada alternativa. Idealmente ingresen los parametros con alguna situación real que les haya tocado. 
Quién sabe, quizás las condiciones de arriendo que les estaban ofreciendo eran verdaderamente una ganga!

## Simulación
### Instrucciones generales 
A la izquierda se encuentran los elementos interactivos para modificar la visualización que muestra cuál es la 
alternativa más rentable. Luego de la visualización se muestran elementos importantes que son resultado de los parámetros 
que se seleccionan y servirán para entender cómo se genera la gráfica.
""")
## STREAMLIT

precio_propiedad = st.sidebar.slider(min_value=1000,max_value= 15000, step =100, value = 2000,label="Precio Propiedad", format="%g UF")
precio_arriendo = st.sidebar.slider(min_value=3.0, max_value= 65., step =.5, value = 6.,  label="Precio Arriendo", format="%g UF")

pie = st.sidebar.slider(min_value=10, max_value= 100, step = 5, 
value = 20, label="Porcentaje para pie o para inversión inicial para IA", format="%g%%")*precio_propiedad/100


plazo = st.sidebar.slider(min_value=10,max_value= 30, step= 5, value = 20, format="%g años", label="Plazo")
tasa_interes = st.sidebar.slider(min_value=1.0,max_value= 10.0, step= 0.05,value = 2.8, label="Tasa Interés anual",format="%g%%")/100
plusvalia = st.sidebar.slider(min_value=1.0,max_value= 10.0, step= 0.05,value = 4., label="Plusvalía anual",format="%g%%")/100

rentabilidad_ia_percent = st.sidebar.slider(min_value=1.0,max_value= 10.0, step= 0.05,value = 4., label="Rentabilidad esperada de instrumento alternativo (IA)", format="%g%%")/100
plazo_meses = plazo*12

periodic_tasa_interes = (1+tasa_interes)**(1/12) - 1

st.write("""### Resultado""")
st.write('\n')
st.write('\n')


mes_num = np.arange(plazo_meses)
mes_num = mes_num + 1

amortizacion_cuota_arr = npf.ppmt(tasa_interes/12, mes_num, plazo_meses, pv = -(precio_propiedad-pie))
capital_adeudado = precio_propiedad-pie-np.cumsum(amortizacion_cuota_arr)
interes_cuota_arr = npf.ipmt(tasa_interes/12, mes_num, plazo_meses, pv = -(precio_propiedad-pie))
dividendos = interes_cuota_arr + amortizacion_cuota_arr
dividendo = dividendos[0]

total_pagado_credito = pie + np.cumsum(dividendos)
costo_prepago = capital_adeudado + 1.5*interes_cuota_arr
costo_total =  costo_prepago + total_pagado_credito
list_valorzcn =npf.fv(plusvalia/12, mes_num, pv = -precio_propiedad, pmt =0)
rentabilidad_br = (list_valorzcn - costo_total)

ahorro_mensual = dividendo - precio_arriendo
rentabilidad_ia = npf.fv(rentabilidad_ia_percent/12, mes_num, pv = -pie, pmt =-ahorro_mensual)
rentabilidad_arrendar = rentabilidad_ia - pie

ahorro_mensual = round(ahorro_mensual, 2)
dividendo = round(dividendo, 2)


df = pd.DataFrame({'Año':mes_num/12,  'Propiedad valorizada':list_valorzcn, 
'Gasto crédito acumulado': total_pagado_credito, 'Amortización':  amortizacion_cuota_arr, 
'Interés($)':interes_cuota_arr, 'Costo Arriendo':precio_arriendo, 'Arrendar': rentabilidad_arrendar, 
'Comprar': rentabilidad_br, "Capital adeudado": capital_adeudado, 'Costo prepago': costo_prepago,
'Costo total': costo_total, 'Rentabilidad IA': rentabilidad_ia, 'Inversión inicial IA': pie})

df = pd.melt(df, id_vars="Año", value_vars=['Propiedad valorizada', 'Costo prepago', 'Arrendar', 
    'Comprar', 'Costo total','Rentabilidad IA', 'Inversión inicial IA'], var_name='Tipo', value_name='UF')

#st.table(df)
def gen_chart(df):

    x_max= df['Año'].max()
    y_min= df[df['Tipo'].isin(['Comprar', 'Arrendar'])]['UF'].min()
    y_max= df[df['Tipo'].isin(['Comprar', 'Arrendar'])]['UF'].max()


    range = ['#006d2c', '#4a1486']
    domain = ["Comprar", 'Arrendar']

    #df
    rtb = alt.Chart(data =df[df['Tipo'].isin(domain)]).mark_line().encode(
    x = alt.X('Año:Q', axis=alt.Axis(title='Año', grid=False), scale= alt.Scale(domain=[0, x_max], nice=False)),
    y = alt.Y('UF:Q', axis=alt.Axis(title='UF', grid=False), scale= alt.Scale(domain=[y_min, y_max], nice=False)),
    color=alt.Color('Tipo:N', scale=alt.Scale(range=range,  domain=domain), legend=alt.Legend(title=None)),
    tooltip=['Tipo',alt.Tooltip('UF', format = ".2f"), alt.Tooltip('Año', format = "d")]
    ).properties(title = 'Rentabilidad de comprar vs arriendar').configure_title(fontSize=20).configure_legend(
    orient='bottom-right'
    ).configure_view(
        strokeWidth=0
    ).interactive()

    range = ['#b2e2e2', '#74c476',  '#006d2c']
    domain = ['Propiedad valorizada', 'Costo total', 'Comprar']

    rtb_c = alt.Chart(data =df[df['Tipo'].isin(domain)]).mark_line().encode(
    x = alt.X('Año:Q', axis=alt.Axis(title='Año', grid=False)),
    y = alt.Y('UF:Q', axis=alt.Axis(title='UF', grid=False)),
    color=alt.Color('Tipo:N', scale=alt.Scale(range=range,  domain=domain), legend=alt.Legend(title=None)),
    tooltip=['Tipo',alt.Tooltip('UF', format = ".2f"), alt.Tooltip('Año', format = "d")]
    ).properties(title = 'Rentabilidad de Comprar').configure_title(fontSize=20).configure_legend(
    orient='bottom-right'
    ).configure_view(
        strokeWidth=0
    ).interactive()

    range = ['#dadaeb','#807dba', '#4a1486']
    domain = ['Rentabilidad IA', 'Inversión inicial IA', 'Arrendar']

    rtb_a = alt.Chart(data =df[df['Tipo'].isin(domain)]).mark_line().encode(
    x = alt.X('Año:Q', axis=alt.Axis(title='Año', grid=False)),
    y = alt.Y('UF:Q', axis=alt.Axis(title='UF', grid=False)),
    color=alt.Color('Tipo:N', scale=alt.Scale(range=range, domain=domain), legend=alt.Legend(title=None)),
    tooltip=['Tipo',alt.Tooltip('UF', format = ".2f"), alt.Tooltip('Año', format = "d")]
    ).properties(title = 'Rentabilidad de Arrendar').configure_title(fontSize=20).configure_legend(
    orient='bottom-right'
    ).configure_view(
        strokeWidth=0
    ).interactive()

    return rtb, rtb_c, rtb_a


rtb, rtb_c, rtb_a= gen_chart(df) #, c
st.altair_chart(rtb, use_container_width=True)

c1,c2, c3 = st.columns(3)

c1.metric(label = 'Pie o Inversión inicial en IA', value =int(pie))
c2.metric(label = 'Dividendo', value =dividendo)
c3.metric(label = 'Ahorro mensual de arriendo', value =ahorro_mensual)

st.write("## Justificación")
st.write("""La gráfica anterior nos muestra con buena claridad que la alternativa más rentable depende de los parámetros 
        elegidos y el momento que las evaluemos. A partir de esto la pregunta que surge, es ¿Cómo, desde los parametros 
        que se obtiene ese resultado?. Para ello dividamos el análisis en 2: Rentabilidad de compra y Rentabilidad de arriendo""")

st.write("### Rentabilidad de comprar")
st.write("La rentabilidad de comprar una propiedad se generó a partir de la siguiente formula")

st.write(r"""$$\footnotesize
                RC_t= PP_t - CP_t- TP_t\\
                RC_t= PP_t - (CP_t + TP_t)\\
                RC_t= PP_t - CT_t\\
                RC_t = \text{Rentabilidad de compra en período t}\\
                PP_t = \text{Precio propiedad al período t}\\
                CP_t = \text{Costo Prepago en período t}\\
                TP_t = \text{Total pagado al período t}\\
                CT_t = \text{Costo total prepagar en período t}\\
                \text{ }\\$$""")
                
st.altair_chart(rtb_c, use_container_width=True)


st.write("### Rentabilidad de arrendar")
st.write("""La rentabilidad por arrendar a simple vista, es un poco más difícil de entender, pero no tanto.
El punto clave es que el sólo hecho de arrendar no genera rentabilidad. Sólo esta ocurre cuando el precio 
de arrendar sea menor al dividendo. Idealmente, además qué ese ahorro se destine a algún instrumento de inversión alternativo 
que nos genere intereses esperados. Cómo por ejemplo un Fondo Mutuo, un depósito a plazo, acciones, bitcoin, etc. 

En este caso la figura es cómo sigue, en vez de utilizar el dinero para pie de la propiedad, se inyecta en este instrumento de inversión
alternativo (IA). A su vez, todo ahorro por concepto de pagar un menor precio de arriendo que el dividendo, 
se depositará en el IA, con la espera que nos genere intereses a medida que pase el tiempo.""")

st.write(r"""$$\footnotesize
                RA_t= RIA_t - II\\
                RC_t = \text{Rentabilidad acumulada de arrendar en período t}\\
                RIA_t = \text{Rentabilidad acumulada de instrumento de inversión alternativa al período t}\\
                II = \text{Inversión inicial en instrumento altenativo}\\
                \text{ }\\$$""")

st.altair_chart(rtb_a, use_container_width=True)

