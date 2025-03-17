from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time
import json
import os
import datetime

def scrape_usr_cloud():
    # 创建日期文件夹
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    date_folder = os.path.join(os.path.dirname(__file__), 'data_date', today)
    os.makedirs(date_folder, exist_ok=True)

    # 配置Chrome选项
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-gpu')
    
    driver = webdriver.Chrome(options=chrome_options)
    
    try:
        # 登录过程
        driver.get("https://account.usr.cn/#/login?type=mp_scada")
        wait = WebDriverWait(driver, 20)
        
        # 读取配置文件
        config_path = os.path.join(os.path.dirname(__file__), 'docs', 'config.json')
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        # 登录
        username_input = wait.until(EC.presence_of_element_located((By.XPATH, "//input[@placeholder='手机号码/邮箱/用户名']")))
        username_input.send_keys(config['username'])
        
        password_input = wait.until(EC.presence_of_element_located((By.XPATH, "//input[@placeholder='密码']")))
        password_input.send_keys(config['password'])
        
        login_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(@class, 'login')]")))
        driver.execute_script("arguments[0].scrollIntoView();", login_button)
        time.sleep(1)
        login_button.click()
        
        # 等待登录完成并跳转
        time.sleep(5)
        
        # 循环处理每个传感器
        for sensor in config['sensors']:
            print(f"\n正在处理: {sensor['name']}")
            
            # 打开新的数据历史页面
            data_history_url = sensor['url']
            driver.execute_script(f"window.open('{data_history_url}', '_blank');")
            
            # 切换到新打开的标签页
            time.sleep(2)
            driver.switch_to.window(driver.window_handles[-1])
            
            # 等待页面加载完成
            time.sleep(5)
            
            # 点击时间选择器图标
            time_picker = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".el-input__icon.el-range__icon.el-icon-time")))
            driver.execute_script("arguments[0].click();", time_picker)
            time.sleep(2)  # 等待时间选择器打开
            
            # 点击"最近1天"
            recent_day_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(@class, 'el-picker-panel__shortcut') and text()='最近1天']")))
            driver.execute_script("arguments[0].click();", recent_day_button)
            time.sleep(1)  # 等待时间选择器更新
            
            # 点击查询按钮
            query_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".el-button.search-btn.el-button--primary.el-button--small")))
            driver.execute_script("arguments[0].click();", query_button)
            print("已点击查询按钮")
            time.sleep(5)  # 等待查询结果加载
            
            # 获取表格数据
            print("正在获取表格数据...")
            
            # 获取所有表格数据
            table_data = driver.execute_script("""
                var result = [];
                
                // 获取所有表格数据
                var tables = document.querySelectorAll('table');
                for (var i = 0; i < tables.length; i++) {
                    var rows = tables[i].querySelectorAll('tr');
                    var tableData = [];
                    
                    for (var j = 0; j < rows.length; j++) {
                        var cells = rows[j].querySelectorAll('td, th');
                        var rowData = [];
                        
                        for (var k = 0; k < cells.length; k++) {
                            rowData.push(cells[k].textContent.trim());
                        }
                        
                        if (rowData.length > 0) {
                            tableData.push(rowData);
                        }
                    }
                    
                    if (tableData.length > 0) {
                        result.push(tableData);
                    }
                }
                
                return result;
            """)
            
            if table_data:
                try:
                    # 只保留第1和第4项元素（索引为0和3）
                    if len(table_data) >= 4:
                        filtered_data = [table_data[0], table_data[3]]
                    else:
                        # 如果数据不足4项，则使用可用的数据
                        filtered_data = [table_data[0], table_data[-1]]
                    
                    # 获取表头
                    headers = filtered_data[0][0][:2]  # 取前两个元素作为表头
                    
                    # 获取数据行
                    rows = filtered_data[1]
                    
                    # 创建格式化的数据字符串
                    formatted_data = f"{headers[1]}\t{headers[0]}\n"  # 表头行
                    for row in rows:
                        if len(row) >= 2:  # 确保行有足够的数据
                            formatted_data += f"{row[0]}\t{row[1]}\n"  # 数据行
                    
                    # 保存为txt文件
                    txt_file_path = os.path.join(date_folder, f"{sensor['name']}.txt")
                    with open(txt_file_path, "w", encoding="utf-8") as f:
                        f.write(formatted_data)
                    print(f"已处理并保存数据到 {txt_file_path}")
                    
                except Exception as e:
                    print(f"处理数据时出错: {str(e)}")
            else:
                print("未找到表格数据")
            
            # 关闭当前标签页，回到主页面
            driver.close()
            driver.switch_to.window(driver.window_handles[0])
            time.sleep(2)

    except Exception as e:
        print(f"执行过程中出现错误: {str(e)}")
    finally:
        driver.quit()

if __name__ == "__main__":
    scrape_usr_cloud()