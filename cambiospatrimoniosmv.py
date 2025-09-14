import streamlit as st
import requests
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# URL de la API
url = "https://mvnet.smv.gob.pe/SMV.OData.Api/api/InfFinanciera/CambiosPatrimonioSMV?sEjercicio=2025&sPeriodo=1&sTipoInf=I&sRpj=B80004"

st.title("Cambios Patrimoniales SMV")

try:
    response = requests.get(url)
    response.raise_for_status()
    data = response.json()

    if data and 'data' in data and isinstance(data['data'], list):
        df = pd.DataFrame(data['data'])
        st.success("Datos cargados exitosamente.")
        st.write("Vista previa del DataFrame:")
        st.dataframe(df.head())

        # Filtrar registros donde DescripcionCuenta comienza con 'SALDOS'
        df_saldos = df[df['DescripcionCuenta'].str.startswith('SALDOS')].copy()

        # Ordenar por OrdenColumna de forma descendente
        df_saldos_sorted_orden_desc = df_saldos.sort_values(by='OrdenColumna', ascending=False)

        # Mostrar registros por DescripcionColumna
        unique_descripcion_columna_in_sorted = df_saldos_sorted_orden_desc['DescripcionColumna'].unique()

        for descripcion_columna_value in unique_descripcion_columna_in_sorted:
            st.subheader(f"Registros para DescripcionColumna: {descripcion_columna_value}")
            filtered_df_by_desc = df_saldos_sorted_orden_desc[
                df_saldos_sorted_orden_desc['DescripcionColumna'] == descripcion_columna_value
            ]
            st.dataframe(filtered_df_by_desc)

        # Gráficos por OrdenColumna
        unique_orden_columna_saldos = df_saldos_sorted_orden_desc['OrdenColumna'].unique()

        for orden_columna_value in unique_orden_columna_saldos:
            st.subheader(f"Gráfico de Monto1 por DescripcionCuenta para OrdenColumna: {orden_columna_value}")
            filtered_df_by_orden = df_saldos_sorted_orden_desc[
                df_saldos_sorted_orden_desc['OrdenColumna'] == orden_columna_value
            ]

            if not filtered_df_by_orden.empty:
                fig, ax = plt.subplots(figsize=(12, max(4, len(filtered_df_by_orden) * 0.5)))
                sns.barplot(x='Monto1', y='DescripcionCuenta', data=filtered_df_by_orden, ax=ax)
                ax.set_title(f'Monto1 por DescripcionCuenta (Saldos) - OrdenColumna: {orden_columna_value}')
                ax.set_xlabel('Monto1')
                ax.set_ylabel('DescripcionCuenta')
                st.pyplot(fig)
            else:
                st.warning(f"No hay datos para graficar en OrdenColumna: {orden_columna_value}")
    else:
        st.error("La respuesta no contiene el formato esperado o está vacía.")
        st.write("Respuesta completa:")
        st.json(data)

except requests.exceptions.RequestException as e:
    st.error(f"Error al obtener datos desde el endpoint: {e}")
except ValueError as e:
    st.error(f"Error al decodificar JSON desde la respuesta: {e}")
except Exception as e:
    st.error(f"Ocurrió un error inesperado: {e}")
