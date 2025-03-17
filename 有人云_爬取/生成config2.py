import json

# 读取传感器名称
with open('传感器.txt', 'r', encoding='utf-8') as f:
    sensor_names = [line.strip() for line in f if line.strip()]

# 读取网址
with open('网址.txt', 'r', encoding='utf-8') as f:
    urls = [line.strip() for line in f if line.strip()]

# 创建传感器数据列表
sensors = []
for i in range(min(len(sensor_names), len(urls))):
    sensor = {
        "name": sensor_names[i],
        "url": urls[i]
    }
    sensors.append(sensor)

# 创建配置字典
config = {
    "sensors": sensors
}

# 将配置保存到config2.json文件
with open('config2.json', 'w', encoding='utf-8') as f:
    json.dump(config, f, ensure_ascii=False, indent=4)

print(f"成功生成config2.json文件，包含{len(sensors)}个传感器数据")