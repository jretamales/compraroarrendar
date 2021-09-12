import streamlit as st
import pandas as pd
import numpy as np
import numpy_financial as npf
import altair as alt



st.write("""# ¿Cuándo me conviene arrendar vs comprar? Un ejercicio simulado.

## Introducción

La respuesta es obvia dirán algunos... Si te alcanza para el pie, siempre conviene comprar!!! 
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
value = 20, label="% para pie o para capital inicial FFMM", format="%g%%")*precio_propiedad/100


plazo = st.sidebar.slider(min_value=10,max_value= 30, step= 5, value = 20, format="%g años", label="Plazo")
tasa_interes = st.sidebar.slider(min_value=1.0,max_value= 10.0, step= 0.05,value = 2.8, label="Tasa Interés anual",format="%g%%")/100
plusvalia = st.sidebar.slider(min_value=1.0,max_value= 10.0, step= 0.05,value = 4., label="Plusvalía anual",format="%g%%")/100

rentabilidad_ffmm = st.sidebar.slider(min_value=1.0,max_value= 10.0, step= 0.05,value = 4., label="Rentabilidad FFMM", format="%g%%")/100
plazo_meses = plazo*12

periodic_tasa_interes = (1+tasa_interes)**(1/12) - 1

st.write("""### Resultado""")

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
rentabilidad_arrendar = npf.fv(rentabilidad_ffmm/12, mes_num, pv = -pie, pmt =-ahorro_mensual)
rentabilidad_arrendar = rentabilidad_arrendar - pie

ahorro_mensual = round(ahorro_mensual, 2)
dividendo = round(dividendo, 2)


df = pd.DataFrame({'Año':mes_num/12,  'Propiedad valorizada':list_valorzcn, 
'Gasto crédito acumulado': total_pagado_credito, 'Amortización':  amortizacion_cuota_arr, 
'Interés($)':interes_cuota_arr, 'Costo Arriendo':precio_arriendo, 'Arrendar': rentabilidad_arrendar, 
'Comprar': rentabilidad_br, "Capital adeudado": capital_adeudado, 'Costo prepago': costo_prepago,
'Costo total': costo_total})

df.to_excel("ca.xlsx")

def gen_chart(df):
    #range = ['red', 'blue', 'green', 'purple']
    #domain = ['Propiedad valorizada', 'Costo prepago', "Comprar", 'Arrendar']

    base = alt.Chart(data = df).transform_fold(
        fold=['Propiedad valorizada', 'Costo prepago', 'Arrendar', 'Comprar'],
        as_=['Tipo', 'UF']
        ).transform_calculate(
            name='"Rentabilidad"'  
        )

    # c = base.transform_filter(
    #     alt.FieldOneOfPredicate(field='Tipo', oneOf=['Propiedad valorizada', 'Costo prepago', 'Capital FFMM'])
    # ).mark_line().encode(
    # x = 'Año:Q',
    # y = 'UF:Q')

    # area = base.mark_area(opacity=0.9).encode(
    #     x='Mes:Q',x2='Mes:Q',
    #     y='Propiedad valorizada:Q',
    #     y2='Costo prepago:Q',
    # color=alt.Color('name:N', scale=alt.Scale(range=range, 
    #     domain=domain), legend=alt.Legend(title=None))
    # )
    # c =c + area
    
    x_max= df['Año'].max()
    y_min= np.min(df[['Comprar', 'Arrendar']].values)
    y_max= np.max(df[['Comprar', 'Arrendar']].values)

    #c.layer[0].encoding.y.title = 'UF'

    range = ['green', 'purple']
    domain = ["Comprar", 'Arrendar']

    rtb = base.transform_filter(
        alt.FieldOneOfPredicate(field='Tipo', oneOf=['Comprar', 'Arrendar'])
    ).mark_line().encode(
    x = alt.X('Año:Q', scale= alt.Scale(domain=[0, x_max], nice=False)),
    y = alt.Y('UF:Q', scale= alt.Scale(domain=[y_min, y_max], nice=False)),
    color=alt.Color('Tipo:N', scale=alt.Scale(range=range, 
    domain=domain), legend=alt.Legend(title=None))
    )

    rtb = rtb.properties(title = 'Rentabilidad de Compra vs Arriendo')

    range = ['green', 'purple']
    domain = ["Comprar", 'Arrendar']

    rtb_c = base.transform_filter(
        alt.FieldOneOfPredicate(field='Tipo', oneOf=['Comprar', 'Arrendar'])
    ).mark_line().encode(
    x = alt.X('Año:Q', scale= alt.Scale(domain=[0, x_max], nice=False)),
    y = alt.Y('UF:Q', scale= alt.Scale(domain=[y_min, y_max], nice=False)),
    color=alt.Color('Tipo:N', scale=alt.Scale(range=range, 
    domain=domain), legend=alt.Legend(title=None))
    )

    rtb_c = rtb_c.properties(title = 'Rentabilidad de Compra vs Arriendo')


    return rtb


res = gen_chart(df) #, c
st.altair_chart(res, use_container_width=True)

c1,c2, c3 = st.columns(3)

c1.metric(label = 'Pie o Capital Inicial FFMM', value =int(pie))
c2.metric(label = 'Dividendo', value =dividendo)
c3.metric(label = 'Ahorro mensual de arriendo', value =ahorro_mensual)

st.write("## Justificación")
st.write("""La gráfica anterior nos muestra con buena claridad que la alternativa más rentable depende de los parámetros 
        elegidos y el momento que las evaluemos. A partir de esto la pregunta que surge, es ¿Cómo, desde los parametros 
        que se obtiene ese resultado?. Para ello dividamos el análisis en 2: Rentabilidad de compra y Rentabilidad de arriendo""")

st.write("### Rentabilidad de compra")
st.write("La rentabilidad de comprar una propiedad se generó a partir de la siguiente formula")

st.write(r"""$$RC_t= PP_t - CP_t- TP_t\\
               RC_t= PP_t - (CP_t + TP_t)\\
               RC_t= PP_t - CT_t\\
                \text{ }\\
                RC_t = \text{Rentabilidad de compra en período t}\\
                PP_t = \text{Precio propiedad al período t}\\
                CP_t = \text{Costo Prepago en período t}\\
                TP_t = \text{Total pagado al período t}\\
                CT_t = \text{Costo total prepagar en período t}\\$$""")
                
