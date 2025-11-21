import json
import os
from PIL import Image

# =========================================================
# 【請修改此處】 設定路徑
# =========================================================
# 存放 LabelMe 產生的 JSON 檔案的資料夾
json_folder = 'path/to/your/labelme_json_folder'
# 存放原始影像的資料夾 (用於取得 W/H)
image_folder = 'path/to/your/original_images'
# 轉換後 YOLO 格式 TXT 檔案的輸出資料夾
yolo_output_folder = 'path/to/yolo_labels_output'

# 確保輸出資料夾存在
os.makedirs(yolo_output_folder, exist_ok=True)

# 假設主動脈瓣的 class_id 為 0 (請根據您的 aoric_valve_colab.yaml 確認)
CLASS_ID = 0

# =========================================================
# 核心轉換函數
# =========================================================
def convert_labelme_to_yolo(json_file_path, image_file_path):
    # 讀取 JSON 檔案
    with open(json_file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # 取得影像的寬度和高度
    img = Image.open(image_file_path)
    W, H = img.size
    
    yolo_lines = []
    
    # 遍歷 JSON 中的所有標籤 (shapes)
    for shape in data['shapes']:
        if shape['shape_type'] == 'rectangle':
            # LabelMe 輸出的是 [x_min, y_min, x_max, y_max] 
            # 座標順序通常是: [左上角座標, 右下角座標]
            points = shape['points']
            
            # 取得像素座標
            x_min = min(points[0][0], points[1][0])
            y_min = min(points[0][1], points[1][1])
            x_max = max(points[0][0], points[1][0])
            y_max = max(points[0][1], points[1][1])

            # 進行標準化轉換 (YOLO格式)
            x_center = (x_min + x_max) / (2 * W)
            y_center = (y_min + y_max) / (2 * H)
            w = (x_max - x_min) / W
            h = (y_max - y_min) / H

            # 格式化輸出字串: [class_id x_center y_center w h]
            yolo_lines.append(f"{CLASS_ID} {x_center:.6f} {y_center:.6f} {w:.6f} {h:.6f}")

    return yolo_lines, data['imagePath']

# =========================================================
# 主運行邏輯
# =========================================================
for filename in os.listdir(json_folder):
    if filename.endswith('.json'):
        json_file_path = os.path.join(json_folder, filename)
        
        # 假設影像檔案名與 JSON 檔案名相同，只是副檔名不同 (例如 .jpg 或 .png)
        # 您需要替換這裡的副檔名，以匹配您的原始 CT 影像格式
        image_name = filename.replace('.json', '.png')  
        image_file_path = os.path.join(image_folder, image_name)

        if not os.path.exists(image_file_path):
            print(f"警告：找不到影像檔案 {image_file_path}，跳過。")
            continue

        yolo_lines, original_image_name = convert_labelme_to_yolo(json_file_path, image_file_path)
        
        # 儲存為 YOLO 格式的 TXT 檔案
        output_txt_name = filename.replace('.json', '.txt')
        output_txt_path = os.path.join(yolo_output_folder, output_txt_name)
        
        with open(output_txt_path, 'w') as f:
            f.write('\n'.join(yolo_lines))
            
        print(f"成功轉換 {filename} -> {output_txt_name}")

print("所有 LabelMe 檔案轉換完成！")