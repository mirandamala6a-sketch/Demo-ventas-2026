import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px

# 1. CONFIGURACIÓN INICIAL
st.set_page_config(layout='wide', page_title="Análisis de Clientes y Productos")

@st.cache_data
def load_data():
    # Asegúrate de que el archivo esté en esta ruta en tu GitHub
    file_path = 'datos/SalidaVentas.xlsx' 
    df = pd.read_excel(file_path)
    if 'Order Date' in df.columns:
        df['Order Date'] = pd.to_datetime(df['Order Date'])
    return df

df = load_data()

# 2. TÍTULO
st.title('👥 Dashboard de Inteligencia de Clientes y Productos')
st.markdown("Análisis detallado del comportamiento de compra y rendimiento de inventario.")

# 3. SIDEBAR - FILTROS DINÁMICOS
st.sidebar.header('Panel de Control')

# Filtro por Segmento de Cliente (Si existe en tu Excel)
if 'Segment' in df.columns:
    segmentos = ['Todos'] + list(df['Segment'].unique())
    sel_segmento = st.sidebar.selectbox('Segmento de Cliente', segmentos)
else:
    sel_segmento = 'Todos'

# Filtro por Categoría
categorias = ['Todas'] + list(df['Category'].unique())
sel_cat = st.sidebar.selectbox('Categoría de Producto', categorias)

# Aplicar Filtros
filtered_df = df.copy()
if sel_segmento != 'Todos':
    filtered_df = filtered_df[filtered_df['Segment'] == sel_segmento]
if sel_cat != 'Todas':
    filtered_df = filtered_df[filtered_df['Category'] == sel_cat]

# 4. MÉTRICAS DE IMPACTO
st.subheader('Métricas de Rendimiento')
m1, m2, m3, m4 = st.columns(4)

with m1:
    st.metric("Total Clientes Únicos", filtered_df['Customer Name'].nunique())
with m2:
    st.metric("Productos Distintos Vendidos", filtered_df['Product Name'].nunique())
with m3:
    st.metric("Ticket Promedio", f"${filtered_df['Sales'].mean():,.2d}")
with m4:
    st.metric("Ganancia Total", f"${filtered_df['Profit'].sum():,.2d}")

st.divider()

# 5. ANÁLISIS DE PRODUCTOS (Gráfica 1 y 2)
col1, col2 = st.columns(2)

with col1:
    st.subheader('🔝 Top 10 Productos Más Vendidos')
    top_productos = filtered_df.groupby('Product Name')['Sales'].sum().sort_values(ascending=False).head(10)
    fig1, ax1 = plt.subplots()
    sns.barplot(x=top_productos.values, y=top_productos.index, palette='Blues_r', ax=ax1)
    ax1.set_xlabel('Ventas Totales')
    st.pyplot(fig1)

with col2:
    st.subheader('💰 Rentabilidad por Categoría')
    # Comparamos Ventas vs Ganancia por Sub-Categoría
    profit_sub = filtered_df.groupby('Sub-Category')[['Sales', 'Profit']].sum().reset_index()
    fig2 = px.scatter(profit_sub, x="Sales", y="Profit", text="Sub-Category", 
                     size="Sales", color="Profit", title="Ventas vs Ganancia")
    st.plotly_chart(fig2, use_container_width=True)

# 6. ANÁLISIS DE CLIENTES (Gráfica 3 y Mapa)
st.divider()
col3, col4 = st.columns([1, 1.5]) # El mapa un poco más ancho

with col3:
    st.subheader('🏆 Top Clientes (Por Volumen)')
    top_clientes = filtered_df.groupby('Customer Name')['Sales'].sum().sort_values(ascending=False).head(10)
    st.table(top_clientes) # Una tabla limpia para ver nombres exactos

with col4:
    st.subheader('📍 Concentración de Ventas (Estados)')
    # Reutilizamos el mapa de calor por estados para ver DÓNDE están los clientes
    state_sales = filtered_df.groupby('State')['Sales'].count().reset_index() # Aquí contamos pedidos
    state_sales.columns = ['State', 'Pedidos']
    
    # Diccionario para abreviaturas (importante para que se vea el mapa)
    us_state_to_abbrev = {"Alabama": "AL", "Alaska": "AK", "Arizona": "AZ", "Arkansas": "AR", "California": "CA", "Colorado": "CO", "Connecticut": "CT", "Delaware": "DE", "Florida": "FL", "Georgia": "GA", "Hawaii": "HI", "Idaho": "ID", "Illinois": "IL", "Indiana": "IN", "Iowa": "IA", "Kansas": "KS", "Kentucky": "KY", "Louisiana": "LA", "Maine": "ME", "Maryland": "MD", "Massachusetts": "MA", "Michigan": "MI", "Minnesota": "MN", "Mississippi": "MS", "Missouri": "MO", "Montana": "MT", "Nebraska": "NE", "Nevada": "NV", "New Hampshire": "NH", "New Jersey": "NJ", "New Mexico": "NM", "New York": "NY", "North Carolina": "NC", "North Dakota": "ND", "Ohio": "OH", "Oklahoma": "OK", "Oregon": "OR", "Pennsylvania": "PA", "Rhode Island": "RI", "South Carolina": "SC", "South Dakota": "SD", "Tennessee": "TN", "Texas": "TX", "Utah": "UT", "Vermont": "VT", "Virginia": "VA", "Washington": "WA", "West Virginia": "WV", "Wisconsin": "WI", "Wyoming": "WY"}
    
    state_sales['Code'] = state_sales['State'].map(us_state_to_abbrev)
    
    fig_map = px.choropleth(state_sales, locations='Code', locationmode='USA-states', 
                            color='Pedidos', scope='usa', color_continuous_scale='GnBu')
    st.plotly_chart(fig_map, use_container_width=True)

# 7. TABLA DE DATOS FILTRADA
st.subheader('🔍 Listado Detallado de Transacciones')
st.dataframe(filtered_df[['Order Date', 'Customer Name', 'Product Name', 'Sales', 'Profit']])
