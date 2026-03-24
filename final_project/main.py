import pandas as pd
import glob

folder = "drive-download-20260324T150705Z-1-001"
files = glob.glob(f"{folder}/*.parquet")
df = pd.concat([pd.read_parquet(f) for f in files], ignore_index=True)

# ============================================
# ИССЛЕДУЕМ 137 ОСТАВШИХСЯ ДУБЛЕЙ
# ============================================
print("=== ИССЛЕДОВАНИЕ 137 ДУБЛЕЙ ===\n")

check_cols = [
    'order_id', 'user_id', 'address_text', 'store_id',
    'created_at', 'paid_at', 'delivery_started_at',
    'delivered_at', 'canceled_at', 'payment_type',
    'order_discount', 'order_cancellation_reason'
]

orders_dedup = df[check_cols].drop_duplicates()
dup_mask = orders_dedup.duplicated(subset=['order_id'], keep=False)
dups = orders_dedup[dup_mask].copy()

print(f"Уникальных order_id с дублями: {dups['order_id'].nunique()}")

# Смотрим один пример детально
example_id = dups['order_id'].iloc[0]
print(f"\nПример order_id = {example_id}:")
print(df[df['order_id'] == example_id][[
    'order_id', 'driver_id', 'delivery_cost',
    'delivered_at', 'canceled_at'
]].drop_duplicates().to_string())

# ============================================
# ПРОВЕРЯЕМ — различаются ли они по delivered_at?
# ============================================
print("\n=== ЧЕМ ОТЛИЧАЮТСЯ ДУБЛИ ===")

# Добавляем driver_id к check_cols
check_with_driver = check_cols + ['driver_id', 'delivery_cost']
full_dedup = df[check_with_driver].drop_duplicates()

# Группируем по order_id и смотрим что различается
dup_orders = dups['order_id'].unique()
example_dups = full_dedup[
    full_dedup['order_id'].isin(dup_orders[:5])
].sort_values('order_id')
print(example_dups.to_string())

# ============================================
# ВЫВОД — отличия только в driver_id и delivery_cost?
# ============================================
print("\n=== ПРОВЕРКА — все дубли из-за смены курьера? ===")

# Для каждого дублированного order_id
# проверяем что отличается ТОЛЬКО driver_id и delivery_cost
non_driver_cols = [c for c in check_cols
                   if c != 'order_id']

problem_orders = []
for oid in dup_orders:
    order_rows = full_dedup[
        full_dedup['order_id'] == oid
    ][non_driver_cols].drop_duplicates()
    if len(order_rows) > 1:
        problem_orders.append(oid)

print(f"Заказов где различаются НЕ только driver/cost: "
      f"{len(problem_orders)}")

if len(problem_orders) > 0:
    print("\nПримеры проблемных заказов:")
    prob = full_dedup[
        full_dedup['order_id'].isin(problem_orders[:3])
    ]
    print(prob.to_string())
else:
    print("✅ Все дубли ТОЛЬКО из-за driver_id/delivery_cost!")

# ============================================
# ФИНАЛЬНЫЙ ВЫВОД — правильная дедупликация orders
# ============================================
print("\n=== ПРАВИЛЬНАЯ ДЕДУПЛИКАЦИЯ ORDERS ===")

# Берём только колонки уровня заказа (без driver и delivery_cost)
orders_final = df[check_cols].drop_duplicates(subset=['order_id'])
print(f"orders после правильной дедупликации: {len(orders_final)}")
print(f"Должно быть 340000: "
      f"{'✅' if len(orders_final) == 340000 else '⚠️'}")

# ============================================
# ФИНАЛЬНЫЕ РАЗМЕРЫ ВСЕХ ТАБЛИЦ
# ============================================
print("\n=== ФИНАЛЬНЫЕ РАЗМЕРЫ ТАБЛИЦ ===")

users = df[['user_id', 'user_phone']].drop_duplicates()
print(f"users:         {len(users):>10}")

stores = df[['store_id', 'store_address']].drop_duplicates()
print(f"stores:        {len(stores):>10}")

drivers = df[['driver_id', 'driver_phone']].drop_duplicates()
print(f"drivers:       {len(drivers):>10}")

items = df[['item_id', 'item_title',
            'item_category']].drop_duplicates()
print(f"items:         {len(items):>10}")

addresses = df[['address_text']].drop_duplicates()
print(f"addresses:     {len(addresses):>10}")

# orders — дедупликация только по order_id
orders = df[check_cols].drop_duplicates(subset=['order_id'])
print(f"orders:        {len(orders):>10}")

# order_drivers — order_id + driver_id + delivery_cost + is_final
od = df[['order_id', 'driver_id', 'delivery_cost',
         'delivered_at']].drop_duplicates()
od = od.copy()
od['is_final'] = od['delivered_at'].notna()
od = od[['order_id', 'driver_id',
         'delivery_cost', 'is_final']].drop_duplicates()
print(f"order_drivers: {len(od):>10}")

# order_items
oi_cols = [
    'order_id', 'item_id', 'item_quantity', 'item_price',
    'item_canceled_quantity', 'item_replaced_id', 'item_discount'
]
order_items = df[oi_cols].drop_duplicates()
print(f"order_items:   {len(order_items):>10}")

print("\n✅ Готово к написанию DDL!")

