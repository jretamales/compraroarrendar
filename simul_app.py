import streamlit as st
import pandas as pd
import numpy as np
import numpy_financial as npf
import altair as alt

st.write("""# ¿Cuándo conviene arrendar ? Un ejercicio simulado.

## Introducción

La respuesta es obvia dirán algunos... Si te alcanza para el pie, nunca conviene arrendar, siempre comprar!!! 
Pero esto es claramente incorrecto. Debe existir una combinación de precio de venta, arriendo, tasa de interés, 
etc., que por más insólita que parezca, haga más conveniente el arriendo. Pero: ¿Cómo encontrar, 
esa combinación cuando las variables son múltiples y con fórmulas que para mucha gente resultan desconocidas 
o demasiado complicadas?. Para resolver esta dificultad, es que generé esta simulación que permite interactuar 
con las variables que determinan cada alternativa. Idealmente hay que ingresar los parámetros con alguna situación 
real que les haya tocado. Quién sabe, quizás las condiciones de arriendo que les estaban ofreciendo eran verdaderamente 
una ganga!

## Simulación
### Instrucciones generales 
A la izquierda en la pantalla, se encuentran los elementos interactivos para modificar la visualización que muestra 
cuál es la alternativa más rentable. Luego de la visualización se muestran elementos importantes que son resultado 
de los parámetros que se seleccionan y servirán para entender el gréfico.
""")
## STREAMLIT

precio_propiedad = st.sidebar.slider(min_value=1000,max_value= 15000, step =100, value = 2000,label="Precio Propiedad", format="%g UF")
precio_arriendo = st.sidebar.slider(min_value=3.0, max_value= 65., step =.5, value = 6.,  label="Precio Arriendo", format="%g UF")

pie = st.sidebar.slider(min_value=10, max_value= 100, step = 5, 
value = 20, label="Porcentaje para pie o para inversión inicial para IA", format="%g%%")*precio_propiedad/100


plazo = st.sidebar.slider(min_value=10,max_value= 30, step= 5, value = 20, format="%g años", label="Plazo")
tasa_interes = st.sidebar.slider(min_value=1.0,max_value= 10.0, step= 0.05,value = 2.8, label="Tasa crédito hipotecario",format="%g%%")/100
plusvalia = st.sidebar.slider(min_value=-1.0,max_value= 10.0, step= 0.05,value = 4., label="Plusvalía anual",format="%g%%")/100

rentabilidad_ia_percent = st.sidebar.slider(min_value=1.0,max_value= 10.0, step= 0.05,value = 4., label="Rentabilidad real esperada de instrumento alternativo (IA)", format="%g%%")/100
mes_extra = st.sidebar.slider(min_value=plazo, max_value= 60, step= 5, value = plazo+5, format="%g años", label="Horizonte de evaluación")
mes_extra = (mes_extra- plazo)*12
correccion_arriendo = st.sidebar.checkbox("¿Corregir precio de arriendo por aumento de plusvalía anual?", value = False)

plazo_meses = plazo*12

periodic_tasa_interes = (1+tasa_interes)**(1/12) - 1

st.sidebar.markdown("### Mini glosario:")
st.sidebar.caption("**IA**: Instrumento de inversión alternativo. Ejemplos: Depósito a plazo, fondo mutuo, acciones, etc.")
st.sidebar.caption("**Plusvalía anual**: Incremento de la valorización del bien raíz o la propiedad")
st.write("""### Resultado""")
st.write('\n')
st.write('\n')

# TODO
# Ajustar mini glosario. 
# Agregar apartado de interpretación de la gráfica

mes_num = np.arange(plazo_meses)
mes_num = mes_num + 1

mes_num_eval = np.arange(plazo_meses+mes_extra)
mes_num_eval = mes_num_eval + 1

amortizacion_cuota_arr = npf.ppmt(tasa_interes/12, mes_num, plazo_meses, pv = -(precio_propiedad-pie))
amortizacion_cuota_arr2 = np.repeat(0, mes_extra)
amortizacion_cuota_arr= np.concatenate((amortizacion_cuota_arr, amortizacion_cuota_arr2), axis=None)

capital_adeudado = precio_propiedad-pie-np.cumsum(amortizacion_cuota_arr)
interes_cuota_arr = npf.ipmt(tasa_interes/12, mes_num, plazo_meses, pv = -(precio_propiedad-pie))
interes_cuota_arr2 = np.repeat(0, mes_extra)
interes_cuota_arr= np.concatenate((interes_cuota_arr, interes_cuota_arr2), axis=None)

seg_inc = [precio_propiedad*0.00018]*(plazo_meses) + [0]*mes_extra
seg_desgrav = capital_adeudado*0.0000852
dividendos = interes_cuota_arr + amortizacion_cuota_arr + seg_inc + seg_desgrav
dividendo = dividendos[0]

total_pagado_credito = pie + np.cumsum(dividendos)
costo_prepago = capital_adeudado + 1.5*interes_cuota_arr
costo_total =  costo_prepago + total_pagado_credito
list_valorzcn =npf.fv(plusvalia/12, mes_num_eval, pv = -precio_propiedad, pmt =0)

rentabilidad_br = (list_valorzcn - costo_total)

dividendos_br2 = np.concatenate((np.repeat(0, plazo_meses), np.repeat(dividendo, mes_extra)), axis =None)
rentabilidad_br2 = npf.fv(rentabilidad_ia_percent/12, mes_num_eval, pv = -dividendos_br2, pmt =0)
rentabilidad_br2 = np.cumsum(rentabilidad_br2)

if correccion_arriendo:
    precio_arriendo = npf.fv(plusvalia/12, mes_num_eval, pv = -precio_arriendo, pmt =0)
    ahorros_mensuales_aux  = dividendo - precio_arriendo
    ahorro_mensual = np.mean(ahorros_mensuales_aux)
else:
    ahorro_mensual = dividendo - precio_arriendo
    ahorros_mensuales_aux = [ahorro_mensual]*(plazo_meses+mes_extra)
    ahorros_mensuales_aux = np.array(ahorros_mensuales_aux)

ahorros_mensuales_aux_cum = np.cumsum(ahorros_mensuales_aux) +pie 
rentabilidad_ia = npf.fv(rentabilidad_ia_percent/12, mes_num_eval, pv = -pie, pmt =-ahorro_mensual)

loc0 = np.where(rentabilidad_ia<=0)[0]
if loc0.size == 0:
    rentabilidad_arrendar = rentabilidad_ia - pie
else:
    rentabilidad_ia = np.concatenate((rentabilidad_ia[:loc0[0]], ahorros_mensuales_aux_cum[loc0[0]:]), axis=None)
    rentabilidad_arrendar = rentabilidad_ia - pie

ahorro_mensual = round(ahorro_mensual, 2)
dividendo = round(dividendo, 2)


df_dict = {'Año':mes_num_eval/12,  'Propiedad valorizada':list_valorzcn, 
'Gasto crédito acumulado': total_pagado_credito, 'Amortización':  amortizacion_cuota_arr, 
'Interés($)':interes_cuota_arr, 'Costo Arriendo':precio_arriendo, 'Arrendar': rentabilidad_arrendar, 
'Comprar': rentabilidad_br+rentabilidad_br2, "Capital adeudado": capital_adeudado, 'Costo prepago': -costo_prepago,
'Costo total de prepago': -costo_total, 'Rentabilidad IA': rentabilidad_ia, 'Inversión inicial IA': -pie, 
'Plazo crédito': [plazo_meses/12]*(plazo_meses+mes_extra), 'Dividendo ahorrado': rentabilidad_br2}

df = pd.DataFrame(df_dict)
df.fillna(0, inplace = True)

df = pd.melt(df, id_vars="Año", value_vars=['Propiedad valorizada', 'Costo prepago', 'Arrendar', 
    'Comprar', 'Costo total de prepago','Rentabilidad IA', 'Inversión inicial IA', 'Dividendo ahorrado'], var_name='Tipo', value_name='UF')

#st.table(df)
def gen_chart(df):

    x_max= df['Año'].max()
    y_min= df[df['Tipo'].isin(['Comprar', 'Arrendar'])]['UF'].min()
    y_max= df[df['Tipo'].isin(['Comprar', 'Arrendar'])]['UF'].max()


    range = ['#2ca02c','#e6550d']
    domain = ["Comprar", 'Arrendar']
    
    base = alt.Chart(data =df[df['Tipo'].isin(domain)])

    rtb = base.mark_line(strokeWidth=5).encode(
    x = alt.X('Año:Q', axis=alt.Axis(title='Año', grid=False), scale= alt.Scale(domain=[0, x_max], nice=False)),
    y = alt.Y('UF:Q', axis=alt.Axis(title='UF', grid=False), scale= alt.Scale(domain=[y_min-100,y_max], nice=False)),
    color=alt.Color('Tipo:N', scale=alt.Scale(range=range,  domain=domain), legend=alt.Legend(
            title=None,symbolStrokeWidth= 7, rowPadding=0., columnPadding=0., padding=0., labelFontSize = 12)),
    tooltip=['Tipo',alt.Tooltip('UF', format = ".2f"), alt.Tooltip('Año', format = "d")]
    )

    rtb = rtb.properties(title = 'Rentabilidad de comprar vs arriendar').configure_title(fontSize=20).configure_legend(
    orient='top-left'
    ).configure_view(
        strokeWidth=0
    ).interactive()


    range = ['#98df8a', '#2ca02c',  '#bcbd22','#c7c7c7']
    domain = ['Propiedad valorizada','Comprar',  'Dividendo ahorrado','Costo total de prepago']
    
    y_min = df[df['Tipo'].isin(domain)]['UF'].min()
    y_max = df[df['Tipo'].isin(domain)]['UF'].max()


    rtb_c = alt.Chart(data =df[df['Tipo'].isin(domain)]).mark_line(strokeWidth=5).encode(
    x = alt.X('Año:Q', axis=alt.Axis(title='Año', grid=False)),
    y = alt.Y('UF:Q', axis=alt.Axis(title='UF', grid=False), scale= alt.Scale(domain=[y_min-100,y_max], nice=False)),
    color=alt.Color(
        'Tipo', scale=alt.Scale(range=range, domain=domain), legend=alt.Legend(
            title=None,symbolStrokeWidth= 7, rowPadding=0., columnPadding=0., padding=0.,labelFontSize = 12)),
    tooltip=['Tipo',alt.Tooltip('UF', format = ".2f"), alt.Tooltip('Año', format = "d")]
    ).properties(title = 'Rentabilidad de Comprar').configure_title(fontSize=20).configure_legend(
    orient='top-left'
    ).configure_view(
        strokeWidth=0
    ).interactive()



    range = ['#fd8d3c','#e6550d',  '#fdd0a2']
    domain = [ 'Rentabilidad IA','Arrendar',  'Inversión inicial IA']
    y_min = df[df['Tipo'].isin(domain)]['UF'].min()
    y_max = df[df['Tipo'].isin(domain)]['UF'].max()

    rtb_a = alt.Chart(data =df[df['Tipo'].isin(domain)]).mark_line(strokeWidth=5).encode(
    x = alt.X('Año:Q', axis=alt.Axis(title='Año', grid=False)),
    y = alt.Y('UF:Q', axis=alt.Axis(title='UF', grid=False), scale= alt.Scale(domain=[y_min-100,y_max], nice=False)),
    color=alt.Color('Tipo:N', scale=alt.Scale(range=range, domain=domain), legend=alt.Legend(title=None,
    symbolStrokeWidth= 7, rowPadding=0., columnPadding=0., padding=0.,labelFontSize = 12)),
    tooltip=['Tipo',alt.Tooltip('UF', format = ".2f"), alt.Tooltip('Año', format = "d")]
    ).properties(title = 'Rentabilidad de Arrendar').configure_title(fontSize=20).configure_legend(
    orient='top-left'
    ).configure_view(
        strokeWidth=0
    ).interactive()

    return rtb, rtb_c, rtb_a


rtb, rtb_c, rtb_a= gen_chart(df) #, c
st.altair_chart(rtb, use_container_width=True)

c1,c2, c3 = st.columns(3)

c1.metric(label = 'Pie o Inversión inicial en IA', value =int(pie))
c2.metric(label = 'Dividendo', value =dividendo)
c3.metric(label = 'Ahorro mensual por arriendo', value =ahorro_mensual)

st.write("## Justificación")
st.write("""La gráfica anterior nos muestra con buena claridad que la alternativa más rentable 
depende de los parámetros elegidos y del momento que las evaluemos. A partir de esto, 
la pregunta que surge es ¿Cómo se obtiene ese resultado desde los parámetros? 
Para ello es necesario dividir el análisis en dos: Rentabilidad de compra y Rentabilidad de arriendo.""")

st.write("""Antes de detallar como se generó la rentabilidad de compra y arriendo es importante precisar que nos
referimos con **rentabilidad**. Para nuestro ejercicio, esto lo entendemos como lo que queda para nuestro bolsillo 
al momento $t$ luego de descontar todo lo que incurrimos (gastando o invirtiendo) para obtenerla. 
Es muy importante tener claridad sobre esta interpretación, porque todo nuestro analisis girará en torno a el.
Para efectos prácticos entonces, desde ahora en adelante cuando nos referimos a rentabilidad **nos referimos a rentabilidad acumulada.**""")
st.write("### Rentabilidad de comprar")

st.write("""La rentabilidad de comprar una propiedad se generó a partir de la siguiente fórmula:""")

st.markdown(r"""$$\footnotesize
                RC_t= PP_t + DA_t - CP_t- TP_t\\
                RC_t= PP_t + DA_t - (CP_t + TP_t)\\
                RC_t= PP_t + DA_t - CT_t\\[4pt]
                RC_t = \text{Rentabilidad de compra en período t}\\
                PP_t = \text{Precio propiedad al período t}\\
                DA_t = \text{Dividendo ahorrado (e invertido) al período t}\\
                CP_t = \text{Costo Prepago en período t}\\
                TP_t = \text{Total pagado al período t}\\
                CT_t = \text{Costo total de prepagar en período t}\\
                \text{ }\\$$""")
                
st.altair_chart(rtb_c, use_container_width=True) 

st.markdown("## Interpretación")
st.write("""<div>Dado lo complejo del gráfico anterior, merece la pena dedicar un par de minutos a explicarlo:
<ul style="margin:0;padding:0">
<li>En <strong><span style="color:#2ca02c">verde</span></strong> se muestra la curva resultante de compra. </li>
<li>El <strong><span style="color:#bcbd22">dividendo ahorrado</span></strong> tiene una forma extraña, la cuál está dada porque
esta variable busca representar cuanto del dividendo podemos ahorrar. Naturalmente, que mientras estemos pagando 
el crédito esto es cero. Sin embargo, una vez que terminamos de pagar, todo el dividendo se ahorra. Cómo suponemos que 
siempre estamos buscando maximizar rentabilidad, lo ahorrado lo invertimos en un instrumento alternativo, que por simplicidad
asumiremos que tiene la misma tasa de rentabilidad elegida en los parámetros. Por ello también la leve curva ascendente.</li>
<li>La curva de <strong><span style="color:#98df8a">propiedad valorizada</span></strong>, es el precio de la propiedad valorizada en el tiempo, calculada mediante valor futuro (ver notas). 
Aquí el supuesto es que el propietario en cualquier momento podría vender la propiedad. El precio al que vendería la propiedad, claramente 
no siempre será el precio en que la compro. Dado a que por lo general, las propiedades se valorizan con el tiempo (plusvalía), 
por lo que se vendería a un precio superior al que le compramos, por ende generando una rentabilidad.</li>
<li>Sin embargo, vender la propiedad implicaría primero saldar o prepagar la deuda con el banco además de incurrir 
en los costos adicionales que exigen los bancos, generalmente entre 1.5 y 2 meses de intereses al momento de prepagar. 
Esto es lo que se representa con la curva <strong><span style="color:#c7c7c7">Costo total de prepago></span></strong>. Pero aparte de eso, esta curva 
incorpora también todo lo que hemos transferido al banco por concepto de intereses</li>
</ul style="margin:0;padding:0">
</div>""", unsafe_allow_html=True)



st.write("### Rentabilidad de arrendar")
st.write("""La rentabilidad por arrendar es, a simple vista, un poco más difícil de entender, pero no tanto. 
El punto clave es que el sólo hecho de arrendar no genera rentabilidad. Esta sólo ocurre cuando el precio de arrendar 
sea menor al dividendo. Idealmente, sería conveniente además que ese ahorro se destine a algún instrumento 
de inversión alternativo que nos genere intereses. Como por ejemplo un fondo mutuo, depósito a plazo, 
compra de acciones, bitcoin, ~~los esquemas primamidales de Rafael Garay o Alberto Chang~~, etc. En este caso la figura es como sigue, en vez de utilizar el dinero 
para el pie de la propiedad, se inyecta en este instrumento de inversión alternativo (IA). 
A su vez, todo ahorro por concepto de pagar un menor precio de arriendo que el dividendo, 
se depositará en el IA, con la esperanza que nos genere intereses a medida que pase el tiempo.
""")

st.markdown(r"""$$\footnotesize
                RA_t= RIA_t - II\\[4pt]
                RC_t = \text{Rentabilidad de arrendar en período t}\\
                RIA_t = \text{Rentabilidad de instrumento de inversión alternativa al período t}\\
                II = \text{Inversión inicial en instrumento altenativo}\\
                \text{ }\\$$""")

st.altair_chart(rtb_a, use_container_width=True)

st.markdown("## Análisis")
st.markdown("""El escenario de opciones es infinito, por algo es que la decisión en muchos casos es compleja. Pero 
dentro de los principales puntos a mencionar: 
* El primer análisis es el más evidentemente pero a la vez más importante. No siempre comprar es lo más conveniente,
pero en muchas veces lo es. Para ello basta con jugar con los parametros para evidenciarlo.
* Otro aspecto relevante, es que no cabe duda que la diferencia entre la plusvalía de la propiedad y 
la rentabilidad esperada del instrumento de inversión alternativo (IA) es un elemento clave para determinar cuál y cuando 
una opción es más rentable que la otra.
* A su vez, algo que no muchas veces se considera pero tiene un efecto importante, es cuando se considera 
que el precio de arriendo no sólo pueda aumentar en virtud de la inflación (UF), también por la plusvalía de la propiedad. 
Si es así, aún con una buen tasa de retorno o rentabilidad IA, es difícil competir contra la alternativa de comprar. Dado
que queda poco márgen para ahorrar e invertir en IA, por consiguiente, arrendar se hace menos atractivo.
*  La simulación inicial por ejemplo (la que se genera al ingresar por primera vez o actualizar la página), 
muestra una situación dónde hasta el año 16 apróx, es más conveniente arrendar. Y, a partir de ahí mostrar,
comprar es más rentable. De ahí es que es tan relevante especificar bien la pregunta, más que ¿Que conviene más?, 
como habitualmente se realiza, es ¿Cuándo conviene más?""")


st.markdown("### Notas")
st.markdown("""Esta es una simplificación del problema y claramente hay otros aspectos que podrían ser tomados en 
cuenta:
* Pago de contribuciones.
* Gastos del crédito hipotecario, tales como: gastos notariales, del conservador, operacionales del banco, etc.
* Comisión para el corredor, en caso que ello aplique.
* Pago de mes de garantía.
* Variaciones en el valor de los seguros de desgravamen e incendios. Para efectos de esta simulación se consideró 
que el cobro por concepto seguro de incendio correspondía a un 0,018% del precio de la propiedad, 
mientras que el seguro de desgravamen representaba un 0,0085% del capital adeudado para cada mes. 
En caso de que los valores sean distintos para su caso, lo importante es intentar hacer coincidir 
el dividendo que se muestra en la simulación. Esa sería una aproximación suficientemente certera.

Aún así, el efecto de estas variables es bastante menor versus los otros elementos considerados.""")

st.markdown("""Adicionalmente, existen aspectos claves implícitos en los cálculos que por efectos de alcance, 
no se detallaron. Para cada uno se incluye un enlace para los que quieran saber más::
* [Cálculo valor futuro.](https://es.wikipedia.org/wiki/Valor_tiempo_del_dinero)
* [Cálculo de dividendos, intereses y amortización.](https://es.wikipedia.org/wiki/Amortizaci%C3%B3n)
""")
