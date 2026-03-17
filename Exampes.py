from nicegui import ui
import plotly.graph_objects as go

"""
product = {
    "id": "SKU123456",                     # 唯一ID
    "name": "无线蓝牙耳机 Pro",
    "price": 299.0,
    "category": "电子产品 > 耳机",
    "brand": "SoundMax",
    "description": "主动降噪，30小时续航，IPX5防水...",
    "images": [
        "https://example.com/headphone1.jpg",
        "https://example.com/headphone2.jpg"
    ],
    "stock": 150,                          # 库存
    "status": "active",                    # active / inactive / sold_out
    "attributes": {                        # 规格
        "颜色": "银色",
        "蓝牙版本": "5.3",
        "充电接口": "USB-C"
    },
    "tags": ["新品", "降噪"],
    "created_at": "2026-03-17T10:00:00Z"
}
"""

# 全局变量：商品总数
all_sp = 0
all_id = ""
all_dzcp = 0
all_fs = 0

names = [
    'Asia', 'Africa', 'Antarctica', 'Europe', 'Oceania',
    'North America', 'South America',
    # 可以再加更多测试滚动
    'Extra 1', 'Extra 2', 'Extra 3', 'Extra 4', 'Extra 5',
    'Extra 6', 'Extra 7', 'Extra 8', 'Extra 9', 'Extra 10',
]



# 创建添加商品对话框
def build_add_window():
    with ui.dialog() as dialog, ui.card().classes('w-96 p-4'):
        ui.label('添加新商品').classes('text-xl font-bold mb-4')

        # 商品名称
        name_input = ui.input(label='商品名称').props('outlined dense').classes('w-full')

        # 分类选择
        category_select = ui.select(
            options=['电子产品', '服饰', '家居', '食品'],
            label='分类'
        ).props('outlined dense').classes('w-full')

        # 价格
        price_input = ui.input(label='价格 (¥)').props('outlined dense type=number').classes('w-full')

        # 按钮组
        with ui.row().classes('w-full justify-end gap-2 mt-4'):
            ui.button('取消', on_click=dialog.close).props('flat')
            ui.button('添加', on_click=lambda: add_product(
                name_input.value,
                category_select.value,
                price_input.value
            )).props('color=accent')

    # 添加商品逻辑
    def add_product(name, category, price):
        if not name or not category or not price:
            ui.notify('请填写完整信息！', type='warning')
            return
        try:
            price = float(price)
            ui.notify(f'✅ 商品 "{name}" 已添加！', type='positive')
            dialog.close()
            # TODO: 这里可以更新全局数据、刷新列表等
        except ValueError:
            ui.notify('价格必须是数字！', type='negative')

    # 返回 dialog 对象
    return dialog


# 创建右侧商品卡
def build_card_blue():
    with ui.card().classes('flex-1 ring-2 ring-blue-500 ...'):
        with ui.column().classes('w-full'):

            ui.label('类型')

            with ui.list().props('dense separator').classes('w-full'):
                ui.item('商品名称')
                ui.item('商品 ID')
                ui.item('价格')
                ui.item('类型 / 分类')

                ui.item('描述（Description）')
                ui.item('主图 / 图片列表')
                ui.item('库存数量')
                ui.item('状态（上架/下架）')
                ui.item('品牌')
                ui.item('规格 / 属性')
                ui.item('创建/更新时间')
                ui.item('标签（Tags）')
                ui.item('评分 / 评论数')

                ui.item('运费模板')
                ui.item('关联商品')
                ui.item('供应商信息')




def build_main_page():
    ui.query('body').style('background-color: #f5f5f5')  # 背景色

    # 声明使用全局变量
    global all_sp
    global all_id
    global all_dzcp
    global all_fs

    # 获取 dialog 引用
    dialog_add_window = build_add_window()

    # 顶层应该是 column：顶部栏 + 主内容区 + 底部状态栏
    with ui.column().classes('w-full h-screen gap-2'): # ← 用 h-screen 占满视口

        # 1. 顶部搜索栏
        with ui.card().classes('w-full flex flex-row'):
            with ui.row().classes('w-full items-center  justify-between px-4 py-2'):  # 保持垂直居中 而不是 px-150

                # 搜索框
                with ui.input(placeholder='商品搜索...').props('rounded outlined dense').classes(
                        'flex-1') as searchinput:
                    with searchinput.add_slot('prepend'):
                        ui.icon('search')
                    with searchinput.add_slot('append'):
                        ui.icon('close').props('flat dense')

                #按钮 dialog
                ui.colors(accent='#6AD4DD')
                ui.button(icon='dashboard_customize', on_click=lambda:dialog_add_window.open()).props(
                    'fab-mini color=accent').classes('ml-auto')

        # 父容器：启用等高拉伸
        with ui.row().classes('w-full gap-2 items-stretch'):  # ← 关键：加 items-stretch 等高拉伸

            # 左侧卡片（占 1 份）
            with ui.card().classes(' flex-[1] '):
                with ui.column().classes('w-full flex flex-[1]'):
                    ui.label("分类筛选:").classes('text-lg')

                    ui.label(f'类型: {all_sp}')
                    ui.select(names, multiple=True, value=names[:2]).classes('w-full').props(
                        'outlined')  # ← 关键：w-full 而不是 w-64

                    ui.label(f'品类: {all_dzcp}')
                    ui.select(names, multiple=True, value=names[:2]).classes('w-full').props(
                        'outlined')  # ← 关键：w-full 而不是 w-64

                    ui.label(f'单品: {all_fs}')
                    ui.select(names, multiple=True, value=names[:2]).classes('w-full').props('outlined')  # ← 关键：w-full 而不是 w-64

                    ui.label(f'产品ID: {all_id}')
                    id_input = ui.input(placeholder='使用ID查询产品').props('outlined dense').classes('w-full')

                    ui.label("价格区间:")

                    with ui.row().classes('w-full items-center gap-2'):  # ← gap 控制间距
                        min_input = ui.input(placeholder='最低').props('outlined dense').classes('flex-1')
                        ui.label('-').classes('text-gray-500')  # 自然宽度
                        max_input = ui.input(placeholder='最高').props('outlined dense').classes('flex-1')

                    ui.button('应用筛选', icon='filter_alt').classes('mt-3 w-full')

            # 右侧卡片（占 5 份）
            with ui.card().classes('flex-[2]  '):
                with ui.column().classes('w-full '):
                    ui.label("库存详情:").classes('text-lg')

                # 👇 让右侧卡片内部内容可滚动，但卡片本身高度 = 左侧
                with ui.scroll_area().classes('h-full w-full scroll-mt-0 scroll-ml-0'):  # ← h-full 很重要！

                    with ui.grid(columns=1).classes('w-full ') as blue_grid:
                        build_card_blue()
                        build_card_blue()


            with ui.card().classes('flex-[2]  '):
                with ui.column().classes('w-full '):
                    with ui.column().classes('w-full '):

                        ui.label("智能分析:").classes('text-lg')
                        with ui.column().classes('w-full '):
                            with ui.grid(columns=3).classes('w-full '):
                                
                                # 图表
                                echart = ui.echart({
                                    'xAxis': {'type': 'value'},
                                    'yAxis': {'type': 'category', 'data': ['A', 'B'], 'inverse': True},
                                    'legend': {'textStyle': {'color': 'gray'}},
                                    'series': [
                                        {'type': 'bar', 'name': 'Alpha', 'data': [0.1, 0.2]},
                                        {'type': 'bar', 'name': 'Beta', 'data': [0.3, 0.4]},
                                    ],
                                })

                                # 图表
                                fig = go.Figure(go.Scatter(x=[1, 2, 3, 4], y=[1, 2, 3, 2.5]))
                                fig.update_layout(margin=dict(l=0, r=0, t=0, b=0))
                                ui.plotly(fig).classes('w-full h-40')


                                #图表
                                ui.echart({
                                    'legend': {
                                        'triggerEvent': True,
                                    },
                                    'radar': {
                                        'triggerEvent': True,
                                        'indicator': [{'name': name, 'max': 100} for name in ['A', 'B', 'C']],
                                    },
                                    'series': [{
                                        'type': 'radar',
                                        'data': [{'name': 'Test', 'value': [77.0, 50.0, 90.0]}],
                                    }],
                                }, on_click=ui.notify)

                            ui.card().classes('flex-[2]  ')


        with ui.card().classes('w-full'):
            with ui.row().classes('w-full  px-4 gap-2 mt-1'):  # 高度增加到 5rem (80px)
                # 卡片1：商品总量 + 状态
                with ui.card().classes('flex-1 flex items-center justify-center text-center p-2'):
                    ui.label(f'📦 商品总数：').classes('text-sm font-medium')
                    ui.label(f'✅ 上架：').classes('text-xs text-green-600')
                    ui.label(f'⚠️ 下架：').classes('text-xs text-gray-500')

                # 卡片2：库存健康度
                with ui.card().classes('flex-1 flex items-center justify-center text-center p-2'):
                    ui.label(f'🧺 总库存： 件').classes('text-sm font-medium')
                    ui.label(f'🚨 缺货： 件').classes('text-xs text-red-600')
                    ui.label(f'📉 低库存： 件').classes('text-xs text-orange-600')

                # 卡片3：筛选 + 价格 + 更新
                with ui.card().classes('flex-1 flex items-center justify-center text-center p-2'):
                    ui.label('🔍 已筛选：电子产品').classes('text-sm')
                    ui.label('💰 ¥0 - ¥10000').classes('text-xs text-purple-600')
                    ui.label('🕒 刚刚更新').classes('text-xs text-gray-500')


build_main_page()
ui.run(port=8085, reload=True)
