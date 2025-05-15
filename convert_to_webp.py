#!/usr/bin/env python3
import os
import subprocess
from pathlib import Path

# Директория с сайтом
site_dir = "/home/runner/workspace/Mcd"
# Директория для WebP изображений
webp_dir = os.path.join(site_dir, "assets/images/webp")

# Создаем директорию, если её нет
os.makedirs(webp_dir, exist_ok=True)

# Список изображений для конвертации
image_formats = ['.png', '.jpg', '.jpeg', '.gif']

# Получаем список всех файлов изображений в директории
def find_images(directory):
    image_files = []
    for root, _, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            if os.path.splitext(file)[1].lower() in image_formats:
                # Исключаем изображения в директории assets/images/webp
                if "assets/images/webp" not in file_path:
                    image_files.append(file_path)
    return image_files

# Конвертируем изображение в WebP
def convert_to_webp(image_path):
    image_name = os.path.basename(image_path)
    base_name = os.path.splitext(image_name)[0]
    webp_path = os.path.join(webp_dir, f"{base_name}.webp")
    
    # Конвертируем с помощью ImageMagick
    try:
        subprocess.run(
            ["convert", image_path, "-quality", "90", webp_path],
            check=True
        )
        print(f"Converted: {image_path} -> {webp_path}")
        return (image_path, webp_path)
    except subprocess.CalledProcessError as e:
        print(f"Error converting {image_path}: {e}")
        return None

# Находим все изображения в директории
print("Finding images to convert...")
images = find_images(site_dir)
print(f"Found {len(images)} images")

# Конвертируем все изображения
converted_images = []
for image in images:
    result = convert_to_webp(image)
    if result:
        converted_images.append(result)

print(f"Successfully converted {len(converted_images)} images")

# Создаем HTML со всеми конвертированными изображениями
with open(os.path.join(site_dir, "webp_images.html"), "w") as f:
    f.write("<!DOCTYPE html>\n<html>\n<head>\n")
    f.write("<title>WebP Images</title>\n")
    f.write("<style>body{font-family:sans-serif;max-width:1200px;margin:0 auto;padding:20px}table{width:100%;border-collapse:collapse}th,td{border:1px solid #ddd;padding:8px;text-align:left}th{background-color:#f2f2f2}img{max-width:200px;max-height:200px}</style>\n")
    f.write("</head>\n<body>\n")
    f.write("<h1>Converted WebP Images</h1>\n")
    f.write("<table>\n")
    f.write("<tr><th>Original</th><th>WebP</th><th>Original Size</th><th>WebP Size</th><th>Savings</th></tr>\n")
    
    total_original_size = 0
    total_webp_size = 0
    
    for original, webp in converted_images:
        original_size = os.path.getsize(original)
        webp_size = os.path.getsize(webp)
        
        original_kb = original_size / 1024
        webp_kb = webp_size / 1024
        savings_percent = (1 - webp_size / original_size) * 100
        
        total_original_size += original_size
        total_webp_size += webp_size
        
        f.write(f"<tr>\n")
        f.write(f"<td>{os.path.basename(original)}<br><img src='{os.path.relpath(original, site_dir)}' alt='Original'></td>\n")
        f.write(f"<td>{os.path.basename(webp)}<br><img src='{os.path.relpath(webp, site_dir)}' alt='WebP'></td>\n")
        f.write(f"<td>{original_kb:.2f} KB</td>\n")
        f.write(f"<td>{webp_kb:.2f} KB</td>\n")
        f.write(f"<td>{savings_percent:.2f}%</td>\n")
        f.write(f"</tr>\n")
    
    # Добавляем итоговую строку
    total_savings_percent = (1 - total_webp_size / total_original_size) * 100
    f.write("<tr style='font-weight:bold;background-color:#f9f9f9'>\n")
    f.write("<td colspan='2'>Total</td>\n")
    f.write(f"<td>{total_original_size/1024:.2f} KB</td>\n")
    f.write(f"<td>{total_webp_size/1024:.2f} KB</td>\n")
    f.write(f"<td>{total_savings_percent:.2f}%</td>\n")
    f.write("</tr>\n")
    
    f.write("</table>\n")
    f.write("</body>\n</html>")

# Создаем JavaScript-файл с картами соответствия изображений
with open(os.path.join(site_dir, "assets/js/image-map.js"), "w") as f:
    f.write("// Карта соответствия оригинальных изображений и WebP\n")
    f.write("const IMAGE_MAP = {\n")
    
    for original, webp in converted_images:
        rel_original = os.path.relpath(original, site_dir)
        rel_webp = os.path.relpath(webp, site_dir)
        f.write(f"  '{rel_original}': '{rel_webp}',\n")
    
    f.write("};\n\n")
    
    # Добавляем функцию для поддержки WebP
    f.write("// Проверяем поддержку WebP\n")
    f.write("function checkWebPSupport() {\n")
    f.write("  const canvas = document.createElement('canvas');\n")
    f.write("  if (canvas.getContext && canvas.getContext('2d')) {\n")
    f.write("    return canvas.toDataURL('image/webp').indexOf('data:image/webp') === 0;\n")
    f.write("  }\n")
    f.write("  return false;\n")
    f.write("}\n\n")
    
    # Добавляем функцию для замены изображений
    f.write("// Заменяем изображения на WebP, если браузер поддерживает\n")
    f.write("function useWebPImages() {\n")
    f.write("  if (checkWebPSupport()) {\n")
    f.write("    document.addEventListener('DOMContentLoaded', () => {\n")
    f.write("      const images = document.querySelectorAll('img');\n")
    f.write("      images.forEach(img => {\n")
    f.write("        const src = img.getAttribute('src');\n")
    f.write("        if (IMAGE_MAP[src]) {\n")
    f.write("          img.setAttribute('src', IMAGE_MAP[src]);\n")
    f.write("        }\n")
    f.write("      });\n")
    f.write("      \n")
    f.write("      // Заменяем фоновые изображения в CSS\n")
    f.write("      const elementsWithBackgroundImage = document.querySelectorAll('[style*=\"background-image\"]');\n")
    f.write("      elementsWithBackgroundImage.forEach(el => {\n")
    f.write("        const style = el.getAttribute('style');\n")
    f.write("        if (style) {\n")
    f.write("          const urlMatch = style.match(/url\\(['\"](.*?)['\"]\\)/);\n")
    f.write("          if (urlMatch && urlMatch[1] && IMAGE_MAP[urlMatch[1]]) {\n")
    f.write("            const newStyle = style.replace(urlMatch[1], IMAGE_MAP[urlMatch[1]]);\n")
    f.write("            el.setAttribute('style', newStyle);\n")
    f.write("          }\n")
    f.write("        }\n")
    f.write("      });\n")
    f.write("    });\n")
    f.write("  }\n")
    f.write("}\n\n")
    
    # Автоматически вызываем функцию
    f.write("// Автоматически вызываем функцию замены изображений\n")
    f.write("useWebPImages();\n")

print("Generated image map JavaScript file")
print(f"Total original size: {total_original_size/1024:.2f} KB")
print(f"Total WebP size: {total_webp_size/1024:.2f} KB")
print(f"Total savings: {total_savings_percent:.2f}%")