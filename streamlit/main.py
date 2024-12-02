import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import timedelta
from carregamento_dados import carregar_dados
from dados_preprocessamento import preprocessar_dados

st.set_page_config(
    page_title='Dashboard de Vendas - Olist',
    page_icon=':bar_chart:',
    layout='wide'
)

clientes, itens_pedidos, pagamentos_pedidos, avaliacoes_pedidos, pedidos, produtos, traducao_categorias = carregar_dados()
dados = preprocessar_dados(clientes, itens_pedidos, pagamentos_pedidos, avaliacoes_pedidos, pedidos, produtos, traducao_categorias)

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;600;800&family=Roboto:wght@400;700&display=swap');

    .header {
        background-color: #2c3e50;
        padding: 20px;
        text-align: center;
        border-radius: 10px;
        font-size: 50px;
        color: white;
        font-family: 'Montserrat', sans-serif;
        margin-bottom: 30px;
    }
    .metric {
        font-size:24px;
        font-weight:600;
        color:#333;
        margin-bottom:5px;
        font-family: 'Montserrat', sans-serif;
    }
    .big-number {
        font-size:25px;
        font-weight:800;
        color:#2980b9;
        font-family: 'Montserrat', sans-serif;
    }
    .card {
        background-color:#ecf0f1;
        padding:20px;
        border-radius:10px;
        text-align:center;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.1);
        margin-bottom:20px;
    }
    div.stTabs [data-baseweb="tab"] {
        font-size: 16px;
        font-family: 'Montserrat', sans-serif;
    }
    div.stTabs [data-baseweb="tab"] > div {
        padding: 8px 16px;
    }
    div.stTabs [role="tablist"] {
        justify-content: center;
    }
    .css-1aumxhk {
        padding-top: 2rem;
    }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<div class='header'>Dashboard de Vendas - Olist</div>", unsafe_allow_html=True)

st.sidebar.title('Filtros')

min_date = dados['order_purchase_timestamp'].min().date()
max_date = dados['order_purchase_timestamp'].max().date()

date_filter_option = st.sidebar.selectbox(
    'Período de Compra',
    options=['Todos', 'Última semana', 'Último mês', 'Último trimestre', 'Último ano', 'Personalizado']
)

today = dados['order_purchase_timestamp'].max().date()

if date_filter_option == 'Todos':
    start_date = min_date
    end_date = max_date
elif date_filter_option == 'Última semana':
    start_date = today - timedelta(days=7)
    end_date = today
elif date_filter_option == 'Último mês':
    start_date = today - timedelta(days=30)
    end_date = today
elif date_filter_option == 'Último trimestre':
    start_date = today - timedelta(days=90)
    end_date = today
elif date_filter_option == 'Último ano':
    start_date = today - timedelta(days=365)
    end_date = today
elif date_filter_option == 'Personalizado':
    default_start_date = max_date - timedelta(days=365)
    if default_start_date < min_date:
        default_start_date = min_date
    start_date = st.sidebar.date_input('Data de Início', min_value=min_date, max_value=max_date, value=default_start_date)
    end_date = st.sidebar.date_input('Data de Fim', min_value=min_date, max_value=max_date, value=max_date)
    if start_date > end_date:
        st.sidebar.error('Data de início deve ser antes da data de fim.')

estados = dados['customer_state'].dropna().unique()
estados_selecionados = st.sidebar.multiselect('Estado', sorted(estados))

categorias = dados['product_category_name_english'].dropna().unique()
categorias_selecionadas = st.sidebar.multiselect('Categoria do Produto', sorted(categorias))

nota_minima = st.sidebar.slider('Nota Mínima de Avaliação', 1, 5, 1)

preco_min = float(dados['price'].min())
preco_max = float(dados['price'].max())
preco_intervalo = st.sidebar.slider(
    'Faixa de Preço',
    min_value=preco_min,
    max_value=preco_max,
    value=(preco_min, preco_max)
)

dados_filtrados = dados[
    (dados['order_purchase_timestamp'].dt.date >= start_date) &
    (dados['order_purchase_timestamp'].dt.date <= end_date) &
    (dados['review_score'] >= nota_minima) &
    (dados['price'] >= preco_intervalo[0]) &
    (dados['price'] <= preco_intervalo[1])
]

if estados_selecionados:
    dados_filtrados = dados_filtrados[dados_filtrados['customer_state'].isin(estados_selecionados)]

if categorias_selecionadas:
    dados_filtrados = dados_filtrados[dados_filtrados['product_category_name_english'].isin(categorias_selecionadas)]

if dados_filtrados.empty:
    st.warning('Nenhum dado disponível para os filtros selecionados. Por favor, ajuste os filtros.')
else:
    with st.container():
        st.markdown("<h2 style='text-align:center; color:#333; font-family:Montserrat;'>Principais Indicadores</h2>", unsafe_allow_html=True)
        col1, col2, col3, col4 = st.columns(4)
        total_vendas = dados_filtrados['price'].sum()
        qtd_pedidos = dados_filtrados['order_id'].nunique()
        clientes_unicos = dados_filtrados['customer_unique_id'].nunique()
        nota_media = dados_filtrados['review_score'].mean()
        with col1:
            st.markdown(f"<div class='card'><div class='metric'>Total de Vendas</div><div class='big-number'>R$ {total_vendas:,.2f}</div></div>", unsafe_allow_html=True)
        with col2:
            st.markdown(f"<div class='card'><div class='metric'>Pedidos</div><div class='big-number'>{qtd_pedidos}</div></div>", unsafe_allow_html=True)
        with col3:
            st.markdown(f"<div class='card'><div class='metric'>Clientes Únicos</div><div class='big-number'>{clientes_unicos}</div></div>", unsafe_allow_html=True)
        with col4:
            st.markdown(f"<div class='card'><div class='metric'>Nota Média</div><div class='big-number'>{nota_media:.2f}</div></div>", unsafe_allow_html=True)
    
    st.markdown("---")
    
    tabs = st.tabs(['Vendas Mensais', 'Vendas por Estado', 'Vendas por Categoria', 'Análise Logística', 'Análise de Clientes', 'Produtos', 'Análise de Pagamentos', 'Avaliações'])
    
    with tabs[0]:
        st.markdown("<h3 style='text-align:center; color:#333; font-family:Montserrat;'>Vendas Mensais</h3>", unsafe_allow_html=True)
        time_freq = st.selectbox('Selecione a Frequência de Tempo', options=['M', 'Q', 'A'], format_func=lambda x: {'M':'Mensal', 'Q':'Trimestral', 'A':'Anual'}[x])
        vendas_tempo = dados_filtrados.set_index('order_purchase_timestamp').resample(time_freq).agg({'price':'sum', 'order_id':'nunique', 'payment_value':'mean'}).reset_index()
        vendas_tempo.rename(columns={'order_id':'Quantidade de Pedidos', 'payment_value':'Ticket Médio'}, inplace=True)
    
        metricas_selecionadas = st.multiselect(
            'Selecione as Métricas para Exibir',
            options=['Vendas', 'Quantidade de Pedidos', 'Ticket Médio'],
            default=['Vendas']
        )
    
        if 'Vendas' in metricas_selecionadas:
            fig_vendas = px.line(
                vendas_tempo,
                x='order_purchase_timestamp',
                y='price',
                labels={'order_purchase_timestamp': 'Data', 'price': 'Vendas (R$)'},
                template='seaborn',
                height=600,
                color_discrete_sequence=['#2980b9']
            )
            fig_vendas.update_traces(line_width=3)
            fig_vendas.update_layout(title='Vendas ao Longo do Tempo', title_x=0.5, xaxis_title='Data', yaxis_title='Vendas (R$)', font=dict(family='Montserrat', size=16))
            st.plotly_chart(fig_vendas, use_container_width=True, key='fig_vendas')
    
        if 'Quantidade de Pedidos' in metricas_selecionadas:
            fig_pedidos = px.bar(
                vendas_tempo,
                x='order_purchase_timestamp',
                y='Quantidade de Pedidos',
                labels={'order_purchase_timestamp': 'Data', 'Quantidade de Pedidos': 'Pedidos'},
                color='Quantidade de Pedidos',
                color_continuous_scale='Blues',
                template='seaborn',
                height=600
            )
            fig_pedidos.update_layout(title='Quantidade de Pedidos ao Longo do Tempo', title_x=0.5, xaxis_title='Data', yaxis_title='Quantidade de Pedidos', font=dict(family='Montserrat', size=16))
            st.plotly_chart(fig_pedidos, use_container_width=True, key='fig_pedidos')
    
        if 'Ticket Médio' in metricas_selecionadas:
            fig_ticket = px.line(
                vendas_tempo,
                x='order_purchase_timestamp',
                y='Ticket Médio',
                labels={'order_purchase_timestamp': 'Data', 'Ticket Médio': 'Ticket Médio (R$)'},
                template='seaborn',
                height=600,
                color_discrete_sequence=['#2980b9']
            )
            fig_ticket.update_traces(line_width=3)
            fig_ticket.update_layout(title='Ticket Médio ao Longo do Tempo', title_x=0.5, xaxis_title='Data', yaxis_title='Ticket Médio (R$)', font=dict(family='Montserrat', size=16))
            st.plotly_chart(fig_ticket, use_container_width=True, key='fig_ticket')
    
        vendas_tempo['Vendas Cumulativas'] = vendas_tempo['price'].cumsum()
        fig_cumulative = px.area(
            vendas_tempo,
            x='order_purchase_timestamp',
            y='Vendas Cumulativas',
            labels={'order_purchase_timestamp': 'Data', 'Vendas Cumulativas': 'Vendas Cumulativas (R$)'},
            template='seaborn',
            height=600,
            color_discrete_sequence=['#2980b9']
        )
        fig_cumulative.update_layout(title='Vendas Cumulativas ao Longo do Tempo', title_x=0.5, xaxis_title='Data', yaxis_title='Vendas Cumulativas (R$)', font=dict(family='Montserrat', size=16))
        st.plotly_chart(fig_cumulative, use_container_width=True, key='fig_cumulative')
    
    with tabs[1]:
        st.markdown("<h3 style='text-align:center; color:#333; font-family:Montserrat;'>Vendas por Estado</h3>", unsafe_allow_html=True)
        estados_disponiveis = dados_filtrados['customer_state'].unique()
        estados_selecionados_vendas = st.multiselect('Selecione os Estados para Visualizar', options=sorted(estados_disponiveis))
        vendas_estado = dados_filtrados.groupby('customer_state')['price'].sum().reset_index()
        vendas_estado = vendas_estado.sort_values('price', ascending=True)
        if estados_selecionados_vendas:
            vendas_estado_filtrado = vendas_estado[vendas_estado['customer_state'].isin(estados_selecionados_vendas)]
        else:
            vendas_estado_filtrado = vendas_estado
        fig_estado = px.bar(
            vendas_estado_filtrado,
            x='price',
            y='customer_state',
            orientation='h',
            labels={'customer_state': 'Estado', 'price': 'Vendas (R$)'},
            color='price',
            color_continuous_scale='Blues',
            template='seaborn',
            height=600
        )
        fig_estado.update_layout(title='Vendas por Estado', title_x=0.5, xaxis_title='Vendas (R$)', yaxis_title='Estado', font=dict(family='Montserrat', size=16))
        st.plotly_chart(fig_estado, use_container_width=True, key='fig_estado')
    
        st.markdown("<h4 style='text-align:center; color:#333; font-family:Montserrat;'>Mapa Interativo de Vendas por Estado</h4>", unsafe_allow_html=True)
        vendas_estado_mapa = vendas_estado_filtrado.copy()
        vendas_estado_mapa['Estado'] = vendas_estado_mapa['customer_state']
        vendas_estado_mapa['Vendas'] = vendas_estado_mapa['price']
        fig_mapa = px.choropleth(
            vendas_estado_mapa,
            geojson='https://raw.githubusercontent.com/codeforamerica/click_that_hood/master/public/data/brazil-states.geojson',
            locations='Estado',
            featureidkey='properties.sigla',
            color='Vendas',
            color_continuous_scale='Blues',
            scope='south america',
            labels={'Vendas': 'Vendas (R$)'},
            template='seaborn',
            height=600
        )
        fig_mapa.update_geos(fitbounds="locations", visible=False)
        fig_mapa.update_layout(title='Mapa de Vendas por Estado', title_x=0.5, font=dict(family='Montserrat', size=16))
        st.plotly_chart(fig_mapa, use_container_width=True, key='fig_mapa')
    
        st.markdown("<h4 style='text-align:center; color:#333; font-family:Montserrat;'>Vendas por Estado e Categoria</h4>", unsafe_allow_html=True)
        vendas_estado_categoria = dados_filtrados.groupby(['customer_state', 'product_category_name_english'])['price'].sum().reset_index()
        if estados_selecionados_vendas:
            vendas_estado_categoria = vendas_estado_categoria[vendas_estado_categoria['customer_state'].isin(estados_selecionados_vendas)]
        fig_sunburst = px.sunburst(
            vendas_estado_categoria,
            path=['customer_state', 'product_category_name_english'],
            values='price',
            color='price',
            color_continuous_scale='Blues',
            labels={'customer_state': 'Estado', 'product_category_name_english': 'Categoria', 'price': 'Vendas (R$)'},
            height=600
        )
        fig_sunburst.update_layout(title='Vendas por Estado e Categoria', title_x=0.5, font=dict(family='Montserrat', size=16))
        st.plotly_chart(fig_sunburst, use_container_width=True, key='fig_sunburst')
    
    with tabs[2]:
        st.markdown("<h3 style='text-align:center; color:#333; font-family:Montserrat;'>Vendas por Categoria</h3>", unsafe_allow_html=True)
        vendas_categoria = dados_filtrados.groupby('product_category_name_english')['price'].sum().reset_index()
        vendas_categoria = vendas_categoria.sort_values('price', ascending=True)
        fig_categoria = px.bar(
            vendas_categoria,
            x='price',
            y='product_category_name_english',
            orientation='h',
            labels={'product_category_name_english': 'Categoria', 'price': 'Vendas (R$)'},
            color='price',
            color_continuous_scale='Blues',
            template='seaborn',
            height=600
        )
        fig_categoria.update_layout(title='Vendas por Categoria', title_x=0.5, xaxis_title='Vendas (R$)', yaxis_title='Categoria', font=dict(family='Montserrat', size=16))
        st.plotly_chart(fig_categoria, use_container_width=True, key='fig_categoria')
    
        fig_disp = px.scatter(
            dados_filtrados,
            x='price',
            y='freight_value',
            color='product_category_name_english',
            hover_data=['product_id'],
            labels={'price': 'Preço (R$)', 'freight_value': 'Valor do Frete (R$)', 'product_category_name_english': 'Categoria'},
            template='seaborn',
            height=600
        )
        fig_disp.update_layout(title='Preço vs. Frete por Categoria', title_x=0.5, font=dict(family='Montserrat', size=16))
        st.plotly_chart(fig_disp, use_container_width=True, key='fig_disp')
    
    with tabs[3]:
        st.markdown("<h3 style='text-align:center; color:#333; font-family:Montserrat;'>Análise Logística</h3>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns(3)
        media_atraso = dados_filtrados['delivery_delay'].mean()
        tempo_entrega_media = dados_filtrados['Tempo de Entrega'].mean()
        percentual_atraso = (dados_filtrados['atraso_entrega'].value_counts(normalize=True).get('Sim', 0) * 100)
        with col1:
            st.markdown(f"<div class='card'><div class='metric'>Atraso Médio (dias)</div><div class='big-number'>{media_atraso:.2f}</div></div>", unsafe_allow_html=True)
        with col2:
            st.markdown(f"<div class='card'><div class='metric'>Tempo Médio de Entrega (dias)</div><div class='big-number'>{tempo_entrega_media:.2f}</div></div>", unsafe_allow_html=True)
        with col3:
            st.markdown(f"<div class='card'><div class='metric'>Pedidos com Atraso (%)</div><div class='big-number'>{percentual_atraso:.2f}%</div></div>", unsafe_allow_html=True)
    
        st.markdown("<h4 style='text-align:center; color:#333; font-family:Montserrat;'>Atraso de Entrega por Estado</h4>", unsafe_allow_html=True)
        atraso_estado = dados_filtrados.groupby('customer_state')['atraso_entrega'].apply(lambda x: (x == 'Sim').mean() * 100).reset_index(name='Percentual de Atraso')
        atraso_estado = atraso_estado.sort_values('Percentual de Atraso', ascending=True)
        fig_atraso_estado = px.bar(
            atraso_estado,
            x='Percentual de Atraso',
            y='customer_state',
            orientation='h',
            labels={'customer_state': 'Estado', 'Percentual de Atraso': 'Percentual de Atraso (%)'},
            color='Percentual de Atraso',
            color_continuous_scale='Blues',
            template='seaborn',
            height=600
        )
        fig_atraso_estado.update_layout(title='Percentual de Pedidos com Atraso por Estado', title_x=0.5, xaxis_title='Percentual de Atraso (%)', yaxis_title='Estado', font=dict(family='Montserrat', size=16))
        st.plotly_chart(fig_atraso_estado, use_container_width=True, key='fig_atraso_estado')
    
        st.markdown("<h4 style='text-align:center; color:#333; font-family:Montserrat;'>Tempo Médio de Entrega por Estado</h4>", unsafe_allow_html=True)
        entrega_estado = dados_filtrados.groupby('customer_state')['Tempo de Entrega'].mean().reset_index()
        entrega_estado = entrega_estado.sort_values('Tempo de Entrega', ascending=True)
        fig_entrega_estado = px.bar(
            entrega_estado,
            x='Tempo de Entrega',
            y='customer_state',
            orientation='h',
            labels={'customer_state': 'Estado', 'Tempo de Entrega': 'Tempo Médio de Entrega (dias)'},
            color='Tempo de Entrega',
            color_continuous_scale='Blues',
            template='seaborn',
            height=600
        )
        fig_entrega_estado.update_layout(title='Tempo Médio de Entrega por Estado', title_x=0.5, xaxis_title='Tempo Médio de Entrega (dias)', yaxis_title='Estado', font=dict(family='Montserrat', size=16))
        st.plotly_chart(fig_entrega_estado, use_container_width=True, key='fig_entrega_estado')
    
        st.markdown("<h4 style='text-align:center; color:#333; font-family:Montserrat;'>Evolução do Tempo Médio de Entrega</h4>", unsafe_allow_html=True)
        entrega_tempo = dados_filtrados.set_index('order_purchase_timestamp').resample('M')['Tempo de Entrega'].mean().reset_index()
        fig_entrega_tempo = px.line(
            entrega_tempo,
            x='order_purchase_timestamp',
            y='Tempo de Entrega',
            labels={'order_purchase_timestamp': 'Data', 'Tempo de Entrega': 'Tempo Médio de Entrega (dias)'},
            template='seaborn',
            height=600
        )
        fig_entrega_tempo.update_layout(title='Evolução do Tempo Médio de Entrega', title_x=0.5, xaxis_title='Data', yaxis_title='Tempo Médio de Entrega (dias)', font=dict(family='Montserrat', size=16))
        st.plotly_chart(fig_entrega_tempo, use_container_width=True, key='fig_entrega_tempo')
    
        st.markdown("<h4 style='text-align:center; color:#333; font-family:Montserrat;'>Relação entre Tempo de Entrega e Avaliação</h4>", unsafe_allow_html=True)
        fig_tempo_avaliacao = px.scatter(
            dados_filtrados,
            x='Tempo de Entrega',
            y='review_score',
            labels={'Tempo de Entrega': 'Tempo de Entrega (dias)', 'review_score': 'Avaliação'},
            template='seaborn',
            height=600
        )
        fig_tempo_avaliacao.update_layout(title='Relação entre Tempo de Entrega e Avaliação', title_x=0.5, xaxis_title='Tempo de Entrega (dias)', yaxis_title='Avaliação', font=dict(family='Montserrat', size=16))
        st.plotly_chart(fig_tempo_avaliacao, use_container_width=True, key='fig_tempo_avaliacao')
    
        st.markdown("<h4 style='text-align:center; color:#333; font-family:Montserrat;'>Mapa de Tempo Médio de Entrega por Estado</h4>", unsafe_allow_html=True)
        entrega_estado_mapa = entrega_estado.copy()
        entrega_estado_mapa['Estado'] = entrega_estado_mapa['customer_state']
        entrega_estado_mapa['Tempo Médio de Entrega'] = entrega_estado_mapa['Tempo de Entrega']
        fig_mapa_entrega = px.choropleth(
            entrega_estado_mapa,
            geojson='https://raw.githubusercontent.com/codeforamerica/click_that_hood/master/public/data/brazil-states.geojson',
            locations='Estado',
            featureidkey='properties.sigla',
            color='Tempo Médio de Entrega',
            color_continuous_scale='Blues',
            scope='south america',
            labels={'Tempo Médio de Entrega': 'Tempo Médio de Entrega (dias)'},
            template='seaborn',
            height=600
        )
        fig_mapa_entrega.update_geos(fitbounds="locations", visible=False)
        fig_mapa_entrega.update_layout(title='Mapa de Tempo Médio de Entrega por Estado', title_x=0.5, font=dict(family='Montserrat', size=16))
        st.plotly_chart(fig_mapa_entrega, use_container_width=True, key='fig_mapa_entrega')
    
    with tabs[4]:
        st.markdown("<h3 style='text-align:center; color:#333; font-family:Montserrat;'>Análise de Clientes</h3>", unsafe_allow_html=True)
        clientes_estado = dados_filtrados.groupby('customer_state')['customer_unique_id'].nunique().reset_index()
        clientes_estado = clientes_estado.sort_values('customer_unique_id', ascending=False).head(10)
        fig_clientes_estado = px.bar(
            clientes_estado,
            x='customer_unique_id',
            y='customer_state',
            orientation='h',
            labels={'customer_state': 'Estado', 'customer_unique_id': 'Número de Clientes'},
            color='customer_unique_id',
            color_continuous_scale='Blues',
            template='seaborn',
            height=600
        )
        fig_clientes_estado.update_layout(title='Top 10 Estados por Número de Clientes', title_x=0.5, xaxis_title='Número de Clientes', yaxis_title='Estado', font=dict(family='Montserrat', size=16))
        st.plotly_chart(fig_clientes_estado, use_container_width=True, key='fig_clientes_estado')
    
        st.markdown("<h4 style='text-align:center; color:#333; font-family:Montserrat;'>Ticket Médio por Estado</h4>", unsafe_allow_html=True)
        ticket_estado = dados_filtrados.groupby('customer_state')['payment_value'].mean().reset_index()
        ticket_estado = ticket_estado.sort_values('payment_value', ascending=True)
        fig_ticket_estado = px.bar(
            ticket_estado,
            x='payment_value',
            y='customer_state',
            orientation='h',
            labels={'customer_state': 'Estado', 'payment_value': 'Ticket Médio (R$)'},
            color='payment_value',
            color_continuous_scale='Blues',
            template='seaborn',
            height=600
        )
        fig_ticket_estado.update_layout(title='Ticket Médio por Estado', title_x=0.5, xaxis_title='Ticket Médio (R$)', yaxis_title='Estado', font=dict(family='Montserrat', size=16))
        st.plotly_chart(fig_ticket_estado, use_container_width=True, key='fig_ticket_estado')
    
        st.markdown('### Detalhes dos Clientes')
        st.dataframe(
            dados_filtrados[
                [
                    'customer_unique_id',
                    'customer_city',
                    'customer_state',
                    'order_id',
                    'price',
                    'review_score'
                ]
            ].drop_duplicates(subset='customer_unique_id').reset_index(drop=True),
            height=400
        )
    
    with tabs[5]:
        st.markdown("<h3 style='text-align:center; color:#333; font-family:Montserrat;'>Análise de Produtos</h3>", unsafe_allow_html=True)
        top_produtos = dados_filtrados.groupby('product_id').agg({
            'product_category_name_english': 'first',
            'price': 'mean',
            'order_id': 'count'
        }).reset_index()
        top_produtos = top_produtos.rename(columns={'order_id': 'Quantidade de Vendas'})
        top_produtos = top_produtos.sort_values('Quantidade de Vendas', ascending=False).head(10)
        fig_top_produtos = px.bar(
            top_produtos,
            x='Quantidade de Vendas',
            y='product_id',
            orientation='h',
            labels={'product_id': 'ID do Produto', 'Quantidade de Vendas': 'Quantidade de Vendas'},
            color='Quantidade de Vendas',
            color_continuous_scale='Blues',
            template='seaborn',
            height=600
        )
        fig_top_produtos.update_layout(title='Top 10 Produtos Mais Vendidos', title_x=0.5, xaxis_title='Quantidade de Vendas', yaxis_title='ID do Produto', font=dict(family='Montserrat', size=16))
        st.plotly_chart(fig_top_produtos, use_container_width=True, key='fig_top_produtos')
    
        st.markdown("<h4 style='text-align:center; color:#333; font-family:Montserrat;'>Vendas por Categoria</h4>", unsafe_allow_html=True)
        vendas_por_categoria = dados_filtrados.groupby('product_category_name_english')['price'].sum().reset_index()
        vendas_por_categoria = vendas_por_categoria.sort_values('price', ascending=True)
        fig_vendas_categoria = px.bar(
            vendas_por_categoria,
            x='price',
            y='product_category_name_english',
            orientation='h',
            labels={'product_category_name_english': 'Categoria', 'price': 'Vendas (R$)'},
            color='price',
            color_continuous_scale='Blues',
            template='seaborn',
            height=600
        )
        fig_vendas_categoria.update_layout(title='Vendas por Categoria', title_x=0.5, xaxis_title='Vendas (R$)', yaxis_title='Categoria', font=dict(family='Montserrat', size=16))
        st.plotly_chart(fig_vendas_categoria, use_container_width=True, key='fig_vendas_categoria')
    
        st.markdown('### Detalhes dos Produtos')
        st.dataframe(
            dados_filtrados[
                [
                    'product_id',
                    'product_category_name_english',
                    'price',
                    'freight_value',
                    'review_score'
                ]
            ].drop_duplicates(subset='product_id').reset_index(drop=True),
            height=400
        )
    
    with tabs[6]:
        st.markdown("<h3 style='text-align:center; color:#333; font-family:Montserrat;'>Análise de Pagamentos</h3>", unsafe_allow_html=True)
    
        total_pagamento = dados_filtrados.groupby('payment_type')['payment_value'].sum().reset_index()
        total_pagamento = total_pagamento.sort_values('payment_value', ascending=False)
        fig_total_pagamento = px.pie(
            total_pagamento,
            names='payment_type',
            values='payment_value',
            title='Total de Vendas por Método de Pagamento',
            color_discrete_sequence=px.colors.sequential.Blues,
            template='seaborn',
            height=600
        )
        fig_total_pagamento.update_layout(title_x=0.5, font=dict(family='Montserrat', size=16))
        st.plotly_chart(fig_total_pagamento, use_container_width=True, key='fig_total_pagamento')
    
        media_pagamento = dados_filtrados.groupby('payment_type')['payment_value'].mean().reset_index()
        media_pagamento = media_pagamento.sort_values('payment_value', ascending=True)
        fig_media_pagamento = px.bar(
            media_pagamento,
            x='payment_value',
            y='payment_type',
            orientation='h',
            labels={'payment_type': 'Método de Pagamento', 'payment_value': 'Valor Médio (R$)'},
            color='payment_value',
            color_continuous_scale='Blues',
            template='seaborn',
            height=600
        )
        fig_media_pagamento.update_layout(title='Valor Médio por Método de Pagamento', title_x=0.5, xaxis_title='Valor Médio (R$)', yaxis_title='Método de Pagamento', font=dict(family='Montserrat', size=16))
        st.plotly_chart(fig_media_pagamento, use_container_width=True, key='fig_media_pagamento')
    
        st.markdown("<h4 style='text-align:center; color:#333; font-family:Montserrat;'>Métodos de Pagamento ao Longo do Tempo</h4>", unsafe_allow_html=True)
        pagamentos_tempo = dados_filtrados.groupby(['payment_type', pd.Grouper(key='order_purchase_timestamp', freq='M')])['payment_value'].sum().reset_index()
        fig_pagamentos_tempo = px.area(
            pagamentos_tempo,
            x='order_purchase_timestamp',
            y='payment_value',
            color='payment_type',
            labels={'order_purchase_timestamp': 'Data', 'payment_value': 'Valor Pago (R$)', 'payment_type': 'Método de Pagamento'},
            template='seaborn',
            height=600
        )
        fig_pagamentos_tempo.update_layout(title='Métodos de Pagamento ao Longo do Tempo', title_x=0.5, xaxis_title='Data', yaxis_title='Valor Pago (R$)', font=dict(family='Montserrat', size=16))
        st.plotly_chart(fig_pagamentos_tempo, use_container_width=True, key='fig_pagamentos_tempo')
    
        st.markdown("<h4 style='text-align:center; color:#333; font-family:Montserrat;'>Correlação entre Método de Pagamento e Avaliação</h4>", unsafe_allow_html=True)
        pagamento_avaliacao = dados_filtrados.groupby(['payment_type', 'review_score']).size().reset_index(name='Quantidade')
        fig_heatmap = px.density_heatmap(
            pagamento_avaliacao,
            x='review_score',
            y='payment_type',
            z='Quantidade',
            color_continuous_scale='Blues',
            template='seaborn',
            labels={'review_score': 'Nota de Avaliação', 'payment_type': 'Método de Pagamento', 'Quantidade': 'Quantidade'}
        )
        fig_heatmap.update_layout(title='Heatmap de Avaliações por Método de Pagamento', title_x=0.5, font=dict(family='Montserrat', size=16))
        st.plotly_chart(fig_heatmap, use_container_width=True, key='fig_heatmap')
    
        st.markdown('### Detalhes dos Pagamentos')
        st.dataframe(
            dados_filtrados[
                [
                    'order_id',
                    'payment_type',
                    'payment_installments',
                    'payment_value'
                ]
            ].drop_duplicates(subset='order_id').reset_index(drop=True),
            height=400
        )
    
    with tabs[7]:
        st.markdown("<h3 style='text-align:center; color:#333; font-family:Montserrat;'>Análise de Avaliações</h3>", unsafe_allow_html=True)
        avaliacoes = dados_filtrados.groupby('review_score').agg({'order_id':'count'}).reset_index()
        avaliacoes.rename(columns={'order_id':'Quantidade'}, inplace=True)
        fig_avaliacoes = px.bar(
            avaliacoes,
            x='review_score',
            y='Quantidade',
            labels={'review_score': 'Nota', 'Quantidade': 'Quantidade'},
            color='Quantidade',
            color_continuous_scale='Blues',
            template='seaborn',
            height=600
        )
        fig_avaliacoes.update_layout(title='Distribuição das Avaliações', title_x=0.5, xaxis_title='Nota', yaxis_title='Quantidade', font=dict(family='Montserrat', size=16))
        st.plotly_chart(fig_avaliacoes, use_container_width=True, key='fig_avaliacoes')
    
        st.markdown("<h4 style='text-align:center; color:#333; font-family:Montserrat;'>Avaliação Média por Categoria</h4>", unsafe_allow_html=True)
        avaliacoes_categoria = dados_filtrados.groupby('product_category_name_english')['review_score'].mean().reset_index()
        avaliacoes_categoria = avaliacoes_categoria.sort_values('review_score', ascending=False)
        fig_avaliacoes_categoria = px.bar(
            avaliacoes_categoria,
            x='review_score',
            y='product_category_name_english',
            orientation='h',
            labels={'product_category_name_english': 'Categoria', 'review_score': 'Avaliação Média'},
            color='review_score',
            color_continuous_scale='Blues',
            template='seaborn',
            height=600
        )
        fig_avaliacoes_categoria.update_layout(title='Avaliação Média por Categoria', title_x=0.5, xaxis_title='Avaliação Média', yaxis_title='Categoria', font=dict(family='Montserrat', size=16))
        st.plotly_chart(fig_avaliacoes_categoria, use_container_width=True, key='fig_avaliacoes_categoria')
    
        st.markdown("<h4 style='text-align:center; color:#333; font-family:Montserrat;'>Evolução da Avaliação Média ao Longo do Tempo</h4>", unsafe_allow_html=True)
        avaliacao_tempo = dados_filtrados.set_index('order_purchase_timestamp').resample('M')['review_score'].mean().reset_index()
        fig_avaliacao_tempo = px.line(
            avaliacao_tempo,
            x='order_purchase_timestamp',
            y='review_score',
            labels={'order_purchase_timestamp': 'Data', 'review_score': 'Avaliação Média'},
            template='seaborn',
            height=600
        )
        fig_avaliacao_tempo.update_layout(title='Evolução da Avaliação Média', title_x=0.5, xaxis_title='Data', yaxis_title='Avaliação Média', font=dict(family='Montserrat', size=16))
        st.plotly_chart(fig_avaliacao_tempo, use_container_width=True, key='fig_avaliacao_tempo')
    
        st.markdown('### Comentários dos Clientes')
        comentarios = dados_filtrados[['review_score', 'review_comment_message', 'product_category_name_english', 'customer_state']].dropna()
        comentarios = comentarios[comentarios['review_comment_message'] != '']
        st.dataframe(comentarios[['review_score', 'review_comment_message', 'product_category_name_english', 'customer_state']].reset_index(drop=True), height=400)
