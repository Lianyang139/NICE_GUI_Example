from nicegui import ui

# ❌ 删除 build_chat_panel() 函数
# ✅ 改用 @ui.page 装饰器

@ui.page('/')
def chat_page():
    """每个用户访问 '/' 时，都会独立执行此函数 → 完全隔离！"""

    async def send() -> None:
        question = text.value
        if not question:
            return
        text.value = ''

        # 显示用户消息（右边）
        with message_container:
            ui.chat_message(text=question, name='You', sent=True)

        # 显示 Bot 消息容器（左边）
        with message_container:
            response_message = ui.chat_message(name='Bot', sent=False)
            spinner = ui.spinner(type='dots')

        # 模拟异步回复
        response = f"你刚才说：{question}"
        await ui.run_javascript('await new Promise(r => setTimeout(r, 800))')
        with response_message:
            ui.markdown(response)
        message_container.remove(spinner)

    # ✅ 所有状态都在函数内部定义 → 每个用户独立！
    message_container = ui.column().classes('w-full max-w-2xl mx-auto flex-grow items-stretch p-2')

    # 输入框
    with ui.footer().classes('bg-white'), ui.column().classes('w-full max-w-3xl mx-auto my-6'):
        text = ui.input(placeholder='输入内容...').props('rounded outlined input-class=mx-3') \
            .classes('w-full self-center').on('keydown.enter', send)

# 启动（不再调用 build_chat_panel()）
ui.run(port=8085, title='Chat App')
