import random
import string

from nicegui import ui
from nicegui.elements.aggrid import aggrid

from product_datatable import ProductTableBase


@ui.page('/')
def data_page():
    ui.label('Ag-Grid Performance Demo').classes('text-2xl mb-4')
    with ui.row().classes('w-full justify-end'):

        ui.button('新增',on_click=lambda: ui.navigate.to('/add'))

    # === 1. 从数据库获取产品 ===
    db = ProductTableBase()

    products= db.get_all_products()
    row_data = [
        {
            "商品ID": raw_product["product_id"],
            "名称": raw_product["product_name"],
            "类别": raw_product["product_type"],
            "品牌": raw_product["product_brand"],
            "售价": raw_product["product_price"],
            "状态": raw_product["product_state"],
            "库存": raw_product["product_num"],
        }
        for raw_product in products
    ]

    headers = ["商品ID", "名称", "类别", "品牌", "售价", "状态", "库存"]
    column_defs = [{'field': name} for name in headers]

    # === 4. 创建 AG Grid ===
    ui.aggrid({
        'columnDefs': column_defs,
        'rowData': row_data,
    }).classes('w-full h-[200px]')  # 高度不用太大

@ui.page('/add')
def add_page():
    ui.label('新增商品页面')

    id_input = ui.input('商品id')
    name_input = ui.input('商品名称')
    type_input = ui.input('商品类型')
    brand_input = ui.input('品牌')
    price_input = ui.input('价格')
    state_input = ui.input('状态')
    num_input = ui.input('库存')

    def add_data_table():
        db = ProductTableBase()

        test_data = {
            "product_id": id_input.value,
            "product_name": name_input.value,
            "product_type": type_input.value,
            "product_brand": brand_input.value,
            "product_price": float(price_input.value or 0),
            "product_state": state_input.value,
            "product_num": int(num_input.value or 0),
        }

        print(test_data)

        db.add_product_data(test_data)

        ui.notify("添加成功")
        ui.navigate.to('/')   # ✅ 关键：固定路径

    with ui.row():
        ui.button('返回', on_click=lambda: ui.navigate.to('/'))
        ui.button('确定', on_click=add_data_table)


ui.run(port=8805,reload=True)


