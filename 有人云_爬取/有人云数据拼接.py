import os
import datetime
import shutil

def merge_sensor_data():
    # 获取项目根目录
    root_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 定义数据源目录和目标目录
    data_date_dir = os.path.join(root_dir, 'data_date')
    data_all_dir = os.path.join(root_dir, 'data_all')
    
    # 确保data_all目录存在
    if not os.path.exists(data_all_dir):
        os.makedirs(data_all_dir)
    
    # 获取所有日期文件夹
    date_folders = [f for f in os.listdir(data_date_dir) if os.path.isdir(os.path.join(data_date_dir, f))]
    
    # 按日期排序文件夹（从旧到新）
    date_folders.sort()
    
    print(f"找到{len(date_folders)}个日期文件夹")
    
    # 用于跟踪已处理的传感器
    processed_sensors = set()
    
    # 遍历每个日期文件夹
    for date_folder in date_folders:
        date_path = os.path.join(data_date_dir, date_folder)
        print(f"\n处理日期文件夹: {date_folder}")
        
        # 获取当前日期文件夹中的所有传感器文件
        sensor_files = [f for f in os.listdir(date_path) if f.endswith('.txt')]
        
        for sensor_file in sensor_files:
            # 传感器名称就是文件名
            sensor_name = sensor_file
            processed_sensors.add(sensor_name)
            
            # 源文件路径
            source_file_path = os.path.join(date_path, sensor_file)
            
            # 目标文件路径
            target_file_path = os.path.join(data_all_dir, sensor_name)
            
            print(f"处理传感器: {sensor_name}")
            
            # 读取源文件数据
            with open(source_file_path, 'r', encoding='utf-8') as source_file:
                source_data = source_file.readlines()
            
            # 如果目标文件已存在，则追加数据（保留表头）
            if os.path.exists(target_file_path):
                with open(target_file_path, 'r', encoding='utf-8') as target_file:
                    target_data = target_file.readlines()
                
                # 获取表头（第一行）
                header = target_data[0]
                
                # 将新数据（跳过表头）追加到现有数据
                with open(target_file_path, 'w', encoding='utf-8') as target_file:
                    # 写入表头
                    target_file.write(header)
                    
                    # 写入现有数据（跳过表头）
                    for line in target_data[1:]:
                        target_file.write(line)
                    
                    # 写入新数据（跳过表头）
                    for line in source_data[1:]:
                        target_file.write(line)
                
                print(f"已将{date_folder}的数据追加到{sensor_name}")
            else:
                # 如果目标文件不存在，则直接复制
                shutil.copy2(source_file_path, target_file_path)
                print(f"已创建新文件{sensor_name}")
    
    print(f"\n数据合并完成，共处理了{len(processed_sensors)}个传感器文件")

if __name__ == "__main__":
    merge_sensor_data()