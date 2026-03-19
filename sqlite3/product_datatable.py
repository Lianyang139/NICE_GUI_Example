# 数据库(增删改查)

import json
import os
import sqlite3
import sys

class ProductTableBase:

    PRODUCT_FIELDS = [
        "product_id",
        "product_name",
        "product_type",
        "product_brand",
        "product_price",
        "product_state",
        "product_num"

    ]

    def __init__(self):

        data_path = os.path.join(get_root_path(), 'data')
        os.makedirs(data_path, exist_ok=True)
        self.file_data = os.path.join(data_path, 'ProductTable.db')

        self.tablebase_init()

    def tablebase_init(self):
        try:
            conn = sqlite3.connect(self.file_data)
            cursor = conn.cursor()

            # IF NOT EXISTS，避免重复运行报错
            create_table_sql = '''
            CREATE TABLE IF NOT EXISTS ProductTable (
                product_id,
                product_name,
                product_type,
                product_brand,
                product_price,
                product_state,
                product_num
            );
            '''
            cursor.execute(create_table_sql)
            conn.commit()
            cursor.close()
            conn.close()
            print("数据库初始化成功")

        except sqlite3.OperationalError:
            print(sqlite3.OperationalError)
            print("数据库初始化失败")


    # 增加
    def add_product_data(self,data:dict)->bool:
        if not all(key in data for key in self.PRODUCT_FIELDS):
            missing = [k for k in self.PRODUCT_FIELDS if k not in data]
            print(f"缺少字段:{missing}")
            return False

        try:
            conn = sqlite3.connect(self.file_data)
            cursor = conn.cursor()

            # 按固定顺序提取值
            values = tuple(data[key] for key in self.PRODUCT_FIELDS)
            print(values)

            # 按长度生成问号
            placeholders = ','.join(['?'] * len(self.PRODUCT_FIELDS))
            print(placeholders)

            # 将元素使用分隔符,生成字符串
            columns = ','.join(self.PRODUCT_FIELDS)
            print(columns)

            cursor.execute(f'''
                INSERT INTO ProductTable ({columns})VALUES ({placeholders})
            ''',values)
            
            conn.commit()
            cursor.close()
            conn.close()
            print("✅ 产品数据插入成功")
            return True
            
        except sqlite3.Error as e:
            print("❌ 插入失败:", e)
            return False

    # 删 根据 ID 删除
    def delete_product(self,product_id):
        conn = sqlite3.connect(self.file_data)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM ProductTable WHERE product_id = ?", (product_id,)) #注意 WHERE 后的 ID
        changed = cursor.rowcount
        conn.commit()
        conn.close()

        if changed > 0:
            print(f"商品 '{product_id}' 已删除")
            return True
        else:
            print(f"商品 '{product_id}' 未找到")
            return False
        '''
        cursor.execute("DELETE FROM ProductTable WHERE product_state = ?", ("下架",))
        cursor.execute("DELETE FROM ProductTable WHERE product_num = 0") 删除所有行 product_num = 0
        cursor.execute("DELETE FROM ProductTable")  # 删除所有行
        '''

    # 改
    def update_product(self, product_id, updates: dict) -> bool:
        # 1. 禁止更新主键
        if 'product_id' in updates:
            raise ValueError("不能更新主键 product_id")

        # 2. 过滤出合法的、可更新的字段（排除主键）
        allowed_fields = set(self.PRODUCT_FIELDS) - {'product_id'}
        invalid_keys = set(updates.keys()) - allowed_fields
        if invalid_keys:
            raise ValueError(f"包含非法字段: {invalid_keys}")

        # 3. 如果没有要更新的字段，直接返回成功
        if not updates:
            return True

        # 4. 构造 SET 子句：`column1 = ?, column2 = ?`
        set_clause = ', '.join([f"{key} = ?" for key in updates.keys()])
        values = list(updates.values()) + [product_id]  # 最后一个是 WHERE 条件的值

        try:
            conn = sqlite3.connect(self.file_data)
            cursor = conn.cursor()

            sql = f"UPDATE ProductTable SET {set_clause} WHERE product_id = ?"
            cursor.execute(sql, values)

            conn.commit()
            cursor.close()
            conn.close()

            # 可选：判断是否真的有行被更新
            if cursor.rowcount == 0:
                print("⚠️ 警告：未找到匹配的 product_id，未更新任何记录")
                return False

            print("✅ 产品更新成功")
            return True

        except sqlite3.Error as e:
            print("❌ 更新失败:", e)
            return False

    # 查询全部数据
    def get_all_products(self)->list:
        conn = sqlite3.connect(self.file_data)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute('''SELECT * FROM ProductTable''') # 表名
        rows = cursor.fetchall()
        conn.close()

        # 将每行转换为字典，并还原 JSON 字段
        products = []
        for row in rows:
            product = dict(row)

            # 不需要 json.loads！原始值已经是正确类型
            # product['id']       = json.loads(product['product_id'])
            # product['name']     = json.loads(product['product_name'])
            # product['type']     = json.loads(product['product_type'])
            # product['brand']    = json.loads(product['product_brand'])
            # product['price']    = json.loads(product['product_price'])
            # product['state']    = json.loads(product['product_state'])
            # product['num']      = json.loads(product['product_num'])

            products.append(product)
        return products

    # 根据ID查询
    def get_product_by_id(self,product_id) -> list:
        conn = sqlite3.connect(self.file_data)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM ProductTable WHERE product_id = ?", (product_id,)) #注意表名:ProductTable
        row = cursor.fetchone()    # 返回一行或 None
        conn.close()

        if row:
            return dict(row)  # 转为字典返回
        else:
            return None  # 或者 raise Exception / 返回空 dict，按需设计

def get_root_path():
    if getattr(sys, 'frozen', False):
        root_path = os.path.dirname(sys.executable)
    else:
        root_path = os.path.dirname(os.path.abspath(__file__))
    return root_path


if __name__ == '__main__':
    db = ProductTableBase()

    test_data = {
        "product_id": "P001",
        "product_name": "无线耳机",
        "product_type": "电子产品",
        "product_brand": "SoundMax",
        "product_price": 299.99,
        "product_state": "新品",
        "product_num": 50
    }

    # 增加
    # db.add_product_data(test_data)

    # 用ID删除
    db.delete_product("P001")

    # 修改
    # sucess = db.update_product('P001',{"product_price": 259.99,
    # "product_num": 30})
    # print('改:',sucess)

    # 查询全部
    res = db.get_all_products()
    print("获取全部:", res)

    # ID 查询
    # res = db.get_product_by_id("P001")
    # print("id获取:", res)


