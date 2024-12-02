import pandas as pd
import streamlit as st

@st.cache_data
def carregar_dados():
    clientes = pd.read_csv('dados/olist_customers_dataset.csv')
    itens_pedidos = pd.read_csv('dados/olist_order_items_dataset.csv')
    pagamentos_pedidos = pd.read_csv('dados/olist_order_payments_dataset.csv')
    avaliacoes_pedidos = pd.read_csv('dados/olist_order_reviews_dataset.csv')
    pedidos = pd.read_csv('dados/olist_orders_dataset.csv')
    produtos = pd.read_csv('dados/olist_products_dataset.csv')
    traducao_categorias = pd.read_csv('dados/product_category_name_translation.csv')
    return clientes, itens_pedidos, pagamentos_pedidos, avaliacoes_pedidos, pedidos, produtos, traducao_categorias
