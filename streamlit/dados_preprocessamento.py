import pandas as pd
import streamlit as st

@st.cache_data
def preprocessar_dados(clientes, itens_pedidos, pagamentos_pedidos, avaliacoes_pedidos, pedidos, produtos, traducao_categorias):
    produtos_com_categoria = produtos.merge(traducao_categorias, on='product_category_name', how='left')
    itens = itens_pedidos.merge(produtos_com_categoria, on='product_id', how='left')
    pedidos_full = pedidos.merge(clientes, on='customer_id', how='left')
    dados = itens.merge(pedidos_full, on='order_id', how='left')
    dados = dados.merge(pagamentos_pedidos, on='order_id', how='left')
    dados = dados.merge(avaliacoes_pedidos[['order_id', 'review_score', 'review_comment_message']], on='order_id', how='left')
    dados['order_purchase_timestamp'] = pd.to_datetime(dados['order_purchase_timestamp'])
    dados['order_approved_at'] = pd.to_datetime(dados['order_approved_at'])
    dados['order_delivered_customer_date'] = pd.to_datetime(dados['order_delivered_customer_date'])
    dados['order_estimated_delivery_date'] = pd.to_datetime(dados['order_estimated_delivery_date'])
    dados['delivery_delay'] = (dados['order_delivered_customer_date'] - dados['order_estimated_delivery_date']).dt.days
    dados['Tempo de Entrega'] = (dados['order_delivered_customer_date'] - dados['order_purchase_timestamp']).dt.days
    dados['atraso_entrega'] = dados['delivery_delay'].apply(lambda x: 'Sim' if x > 0 else 'Não')
    dados['price'] = dados['price'].fillna(0)
    dados['payment_value'] = dados['payment_value'].fillna(0)
    dados['freight_value'] = dados['freight_value'].fillna(0)
    return dados
