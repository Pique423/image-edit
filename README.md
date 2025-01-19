图像水印添加工具 README

一、工具简介

本工具是一个用于为图像添加水印和处理图像信息的Python脚本。它能够读取图像的EXIF信息，根据这些信息生成包含机型、光圈、焦距、快门、ISO等参数的水印，并将水印添加到图像上。同时，还支持对图像进行放大、模糊以及图像拼接等操作。

二、功能特点

1. RAW图像格式支持：利用rawpy库将RAW格式图像转换为可处理的RGB图像格式，方便后续操作。

2. EXIF信息读取：通过exifread库读取图像的EXIF信息，获取机型、光圈、焦距、快门、ISO等参数，用于生成水印内容。

3. 水印生成与添加：根据配置文件和图像尺寸，自适应调整水印的字体大小和位置，将水印添加到图像底部的白色区域。支持添加用户自定义logo和品牌logo。

4. 图像增强操作：提供图像放大、模糊以及图像拼接功能，如将原始图像粘贴到放大并模糊处理后的图像上，生成独特的视觉效果。

三、使用方法

1. 准备工作

• 确保安装了所需的Python库，可通过pip install rawpy Pillow exifread pyyaml命令进行安装。

• 准备好配置文件config.yaml，并根据需求进行配置。配置文件示例如下：
logo:
  enable: true
  brand:
    user_logo:
      path: logo.png
    brand:
      path: brand_logo.png
user:
  name: Whischick
font:
  model: Arial.ttf
  fas: Arial.ttf
  lens: Arial.ttf
  camera_brand: Arial.ttf
  author: Arial.ttf
2. 运行脚本

• 在命令行中进入脚本所在目录。

• 运行脚本，将raw_image_file变量替换为实际的RAW格式照片文件名及路径，如：
if __name__ == "__main__":
    raw_image_file = "IMG_1861.DNG"
    add_sony_a7m4_watermark(raw_image_file)
• 执行脚本后，会在原始图像所在目录生成添加水印后的图像，文件名为原始文件名加上_watermarked.jpg。

四、代码结构说明

1. 函数定义

• load_config：从config.yaml文件中读取配置信息。

• compute_aperture：将光圈值字符串转换为精确的小数表示。

• get_raw：读取RAW格式图像并转换为PIL的Image对象，若格式不支持则直接打开图像。

• get_image_info：读取图像的EXIF信息并提取关键参数。

• watermark_font_size：根据图像尺寸和水印类型计算合适的字体大小。

• watermark_position：根据图像尺寸、水印类型和文本尺寸计算水印的位置。

• hconcat_images和vconcat_images：分别实现水平和垂直方向的图像拼接。

• genarate_watermark：生成包含水印信息的图像，支持添加文本水印和logo。

• logo：在图像上指定位置粘贴logo。

• resize_and_blur_image：对图像进行放大和高斯模糊处理。

• paste_images：将一个图像粘贴到另一个图像的指定位置。

• add_sony_a7m4_watermark：主处理函数，整合图像读取、信息获取、水印生成和图像增强等操作。

• classic_watermark：将生成的水印图像垂直拼接在原始图像下方。

2. 主程序

• 在if __name__ == "__main__":代码块中，指定要处理的图像文件路径，并调用add_sony_a7m4_watermark函数进行图像水印添加和处理。

五、注意事项

1. 确保配置文件config.yaml中的路径和参数正确，特别是字体文件路径和logo文件路径。

2. 处理的图像文件格式需被rawpy和PIL库支持，对于不支持的RAW格式，程序会尝试直接打开，但可能无法获取完整的EXIF信息。

3. 水印位置和字体大小的计算是基于一定的比例和规则，可根据实际需求在代码中调整相关参数以达到更好的效果。