import importlib.util
from typing import TYPE_CHECKING, Literal, cast

from typing_extensions import Self

from ... import helpers, optional_features
from ...awaitable_response import AwaitableResponse
from ...defaults import DEFAULT_PROP, resolve_defaults
from ...dependencies import register_importmap_override
from ...element import Element

# 动态检测是否安装了 pandas，若安装则注册为可选功能
if importlib.util.find_spec('pandas'):
    optional_features.register('pandas')
    if TYPE_CHECKING:
        import pandas as pd

# 动态检测是否安装了 polars，若安装则注册为可选功能
if importlib.util.find_spec('polars'):
    optional_features.register('polars')
    if TYPE_CHECKING:
        import polars as pl


class AgGrid(Element, component='aggrid.js', esm={'nicegui-aggrid': 'dist'}, default_classes='nicegui-aggrid'):
    VERSION = '34.2.0'  # NiceGUI 使用的 AG Grid 版本号

    @resolve_defaults
    def __init__(self,
                 options: dict, *,
                 html_columns: list[int] = DEFAULT_PROP | [],
                 theme: Literal['quartz', 'balham', 'material', 'alpine'] | None = None,
                 auto_size_columns: bool = True,
                 modules: Literal['community', 'enterprise'] | list[str] = 'community',
                 ) -> None:
        """AG Grid 表格组件

        使用 `AG Grid <https://www.ag-grid.com/>`_ 创建高性能数据表格。
        可通过更新 ``options`` 属性将更改推送到前端表格。

        可使用 ``run_grid_method`` 和 ``run_row_method`` 方法与客户端的 AG Grid 实例交互。

        :param options: AG Grid 配置字典（核心参数）
        :param html_columns: 应渲染为 HTML 的列索引列表（默认：空列表）
        :param theme: AG Grid 主题，可选 "quartz"、"balham"、"material" 或 "alpine"
                      （默认：从 options 中取，若无则使用 "quartz"）
        :param auto_size_columns: 是否自动调整列宽以适应表格宽度（默认：True）
        :param modules: 使用的模块类型："community"（社区版）、"enterprise"（企业版），
                        或自定义模块列表（默认："community"）
        """
        # 将 modules 转换为标准模块列表格式
        if not isinstance(modules, list):
            modules = [f'All{modules.capitalize()}Module']

        # 迁移已废弃的 checkboxRenderer（向后兼容，将在 NiceGUI 4.0 移除）
        self._migrate_deprecated_checkbox_renderer(options)

        super().__init__()
        # 合并用户配置与默认配置
        self._props['options'] = {
            'theme': theme or 'quartz',  # 默认主题
            **({'autoSizeStrategy': {'type': 'fitGridWidth'}} if auto_size_columns else {}),
            **options,  # 用户传入的 options 优先级更高
        }
        self._props['html-columns'] = html_columns[:]  # 深拷贝
        self._update_method = 'update_grid'
        self._props['modules'] = modules[:]

        # 兼容旧参数名（将在 4.0 移除）
        self._props.add_rename('html_columns', 'html-columns')

    @staticmethod
    def _migrate_deprecated_checkbox_renderer(options: dict) -> None:
        """将已废弃的 'checkboxRenderer' 迁移到原生布尔渲染器，并警告用户。"""
        migrated = False
        for col in options.get('columnDefs', []):
            if col.get('cellRenderer') == 'checkboxRenderer':
                del col['cellRenderer']
                col['cellDataType'] = 'boolean'  # 使用原生布尔类型
                col['editable'] = True  # 允许编辑
                migrated = True
        if migrated:
            helpers.warn_once(
                "AG Grid: 'checkboxRenderer' 已废弃。\n"
                '您的代码当前包含：\n'
                "    'cellRenderer': 'checkboxRenderer',\n"
                '但推荐使用原生渲染器（更好的无障碍性和样式支持）：\n'
                "    'cellDataType': 'boolean',\n"
                "    'editable': True,\n"
                '请尽快迁移，此兼容性将在 NiceGUI 4.0 中移除。'
            )

    @classmethod
    def from_pandas(cls,
                    df: 'pd.DataFrame', *,
                    html_columns: list[int] = [],  # noqa: B006
                    theme: Literal['quartz', 'balham', 'material', 'alpine'] | None = None,
                    auto_size_columns: bool = True,
                    options: dict = {},  # noqa: B006
                    modules: Literal['community', 'enterprise'] | list[str] = 'community',
                    ) -> Self:
        """从 Pandas DataFrame 创建 AG Grid。

        注意：
        如果 DataFrame 包含不可序列化的列（如 ``datetime64[ns]``、``timedelta64[ns]``、
        ``complex128`` 或 ``period[M]``），它们将被自动转换为字符串。
        如需自定义转换方式，请在传入前手动处理 DataFrame。
        详见 `issue 1698 <https://github.com/zauberzeug/nicegui/issues/1698>`_。

        :param df: Pandas DataFrame
        :param html_columns: 应渲染为 HTML 的列索引（默认：空列表，v2.19.0 新增）
        :param theme: AG Grid 主题（同上）
        :param auto_size_columns: 是否自动调整列宽（默认：True）
        :param options: 额外的 AG Grid 配置项
        :param modules: 模块类型（同上）
        :return: AG Grid 元素实例
        """
        import pandas as pd  # 延迟导入

        def is_special_dtype(dtype):
            return (pd.api.types.is_datetime64_any_dtype(dtype) or
                    pd.api.types.is_timedelta64_dtype(dtype) or
                    pd.api.types.is_complex_dtype(dtype) or
                    isinstance(dtype, pd.PeriodDtype))

        # 找出特殊类型列并转为字符串
        special_cols = df.columns[df.dtypes.apply(is_special_dtype)]
        if not special_cols.empty:
            df = df.copy()
            df[special_cols] = df[special_cols].astype(str)

        # 不支持 MultiIndex 列名
        if isinstance(df.columns, pd.MultiIndex):
            raise ValueError('不支持 MultiIndex 列名。'
                             '可先转换为字符串，例如：'
                             '`df.columns = ["_".join(col) for col in df.columns.values]`.')

        return cls({
            'columnDefs': [{'field': str(col)} for col in df.columns],
            'rowData': df.to_dict('records'),  # 转为字典列表
            'suppressFieldDotNotation': True,  # 支持字段名含点号（如 user.name）
            **options,
            'theme': theme or options.get('theme', 'quartz'),
        }, html_columns=html_columns, theme=theme, auto_size_columns=auto_size_columns, modules=modules)

    @classmethod
    def from_polars(cls,
                    df: 'pl.DataFrame', *,
                    html_columns: list[int] = [],  # noqa: B006
                    theme: Literal['quartz', 'balham', 'material', 'alpine'] | None = None,
                    auto_size_columns: bool = True,
                    options: dict = {},  # noqa: B006
                    modules: Literal['community', 'enterprise'] | list[str] = 'community',
                    ) -> Self:
        """从 Polars DataFrame 创建 AG Grid。

        如果 DataFrame 包含非 UTF-8 数据类型，将自动转换为字符串。
        如需自定义转换，请在传入前手动处理。

        *v2.7.0 新增*

        :param df: Polars DataFrame
        :param html_columns: 应渲染为 HTML 的列索引（默认：空列表，v2.19.0 新增）
        :param theme: AG Grid 主题（同上）
        :param auto_size_columns: 是否自动调整列宽（默认：True）
        :param options: 额外的 AG Grid 配置项
        :param modules: 模块类型（同上）
        :return: AG Grid 元素实例
        """
        return cls({
            'columnDefs': [{'field': str(col)} for col in df.columns],
            'rowData': df.to_dicts(),  # Polars 转字典列表
            'suppressFieldDotNotation': True,
            **options,
            'theme': theme or options.get('theme', 'quartz'),
        }, html_columns=html_columns, theme=theme, auto_size_columns=auto_size_columns, modules=modules)

    # --- 属性访问器（Property Getters/Setters）---

    @property
    def options(self) -> dict:
        """获取当前 AG Grid 配置字典。"""
        return self._props['options']

    @options.setter
    def options(self, value: dict) -> None:
        """设置新的 AG Grid 配置（会触发前端更新）。"""
        self._props['options'] = value

    @property
    def html_columns(self) -> list[int]:
        """获取应渲染为 HTML 的列索引列表。"""
        return self._props['html-columns']

    @html_columns.setter
    def html_columns(self, value: list[int]) -> None:
        """设置应渲染为 HTML 的列索引。"""
        self._props['html-columns'] = value[:]

    @property
    def theme(self) -> Literal['quartz', 'balham', 'material', 'alpine'] | None:
        """获取当前主题。"""
        return self._props['options'].get('theme')

    @theme.setter
    def theme(self, value: Literal['quartz', 'balham', 'material', 'alpine'] | None) -> None:
        """设置新主题。"""
        self._props['options']['theme'] = value

    @property
    def auto_size_columns(self) -> bool:
        """是否启用自动列宽调整。"""
        return self._props['options'].get('autoSize策略', {}).get('type') == 'fitGridWidth'

    @auto_size_columns.setter
    def auto_size_columns(self, value: bool) -> None:
        """动态开启/关闭自动列宽。"""
        if value and not self.auto_size_columns:
            self._props['options']['autoSizeStrategy'] = {'type': 'fitGridWidth'}
        if not value and self.auto_size_columns:
            self._props['options'].pop('autoSizeStrategy', None)

    # --- 客户端 API 交互方法 ---

    def run_grid_method(self, name: str, *args, timeout: float = 1) -> AwaitableResponse:
        """调用 AG Grid 的 Grid API 方法。

        查看完整方法列表：`AG Grid API <https://www.ag-grid.com/javascript-data-grid/grid-api/>`_

        若 await 此方法，将返回调用结果；否则异步执行不等待。

        :param name: 方法名（如 'sizeColumnsToFit'）
        :param args: 方法参数
        :param timeout: 超时时间（秒，默认 1 秒）
        :return: 可 await 的响应对象
        """
        return self.run_method('run_grid_method', name, *args, timeout=timeout)

    def run_row_method(self, row_id: str, name: str, *args, timeout: float = 1) -> AwaitableResponse:
        """对指定行调用 AG Grid 行级 API 方法。

        查看方法列表：`AG Grid Row Reference <https://www.ag-grid.com/javascript-data-grid/row-object/>`_

        :param row_id: 行 ID（由 getRowId 配置定义）
        :param name: 方法名
        :param args: 方法参数
        :param timeout: 超时时间（秒，默认 1 秒）
        :return: 可 await 的响应对象
        """
        return self.run_method('run_row_method', row_id, name, *args, timeout=timeout)

    async def get_selected_rows(self) -> list[dict]:
        """获取当前选中的所有行数据。

        特别适用于配置了 ``rowSelection: 'multiple'`` 的场景。

        :return: 选中行的数据列表
        """
        result = await self.run_grid_method('getSelectedRows')
        return cast(list[dict], result)

    async def get_selected_row(self) -> dict | None:
        """获取当前选中的单一行数据。

        特别适用于配置了 ``rowSelection: 'single'`` 的场景。

        :return: 若有选中行则返回第一行数据，否则返回 None
        """
        rows = await self.get_selected_rows()
        return rows[0] if rows else None

    async def get_client_data(
            self,
            *,
            timeout: float = 1,
            method: Literal['all_unsorted', 'filtered_unsorted', 'filtered_sorted', 'leaf'] = 'all_unsorted'
    ) -> list[dict]:
        """从客户端获取最新数据（包含用户编辑的内容）。

        特别适用于启用了 ``'editable': True`` 的表格。

        注意：单元格编辑后，数据不会立即更新，需退出编辑模式（除非设置了 ``stopEditingWhenCellsLoseFocus: True``）。

        :param timeout: 超时时间（秒）
        :param method: 数据获取方式：
                       - 'all_unsorted': 所有行（未排序）
                       - 'filtered_unsorted': 过滤后的行（未排序）
                       - 'filtered_sorted': 过滤并排序后的行
                       - 'leaf': 仅叶节点（用于树形结构）
        :return: 行数据列表
        """
        API_METHODS = {
            'all_unsorted': 'forEachNode',
            'filtered_unsorted': 'forEachNodeAfterFilter',
            'filtered_sorted': 'forEachNodeAfterFilterAndSort',
            'leaf': 'forEachLeafNode',
        }
        result = await self.client.run_javascript(f'''
            const rowData = [];
            getElement({self.id}).api.{API_METHODS[method]}(node => rowData.push(node.data));
            return rowData;
        ''', timeout=timeout)
        return cast(list[dict], result)

    async def load_client_data(self) -> None:
        """从客户端拉取最新数据并更新服务器端的 rowData。

        用于同步用户在可编辑单元格中的修改。

        注意：同上，需确保单元格已退出编辑模式。
        """
        client_row_data = await self.get_client_data()
        self.options['rowData'] = client_row_data

    @staticmethod
    def set_module_source(url: str) -> None:
        """为所有 AG Grid 元素覆盖 ESM 模块源地址。

        此操作为全局设置，影响所有页面和客户端。
        可用于切换至 AG Grid 企业版或自托管版本。

        :param url: ESM 模块 URL（例如："https://cdn.jsdelivr.net/npm/ag-grid-enterprise@34.2.0/+esm"）
        """
        register_importmap_override('nicegui-aggrid', url)
