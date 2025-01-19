# ImageWaterMark 项目说明
## 一、项目概述
`ImageWaterMark` 是一个用于给图像添加水印的Python项目。该项目支持从RAW格式（如`.ARW`、`.DNG`等）和常见图像格式（如`.jpg`、`.png`等）的文件中读取图像，并添加多种类型的水印，包括文本水印和logo水印。此外，还提供了生成经典白底水印和模糊背景水印的功能。

## 二、功能特性
1. **图像读取**：支持读取RAW格式及常见图像格式的文件，并将其转换为PIL库的`Image`对象。
2. **水印配置**：通过`config.yaml`文件配置水印的相关参数，如logo的启用状态、品牌logo信息、用户信息、字体等。
3. **文本水印添加**：从图像的EXIF信息中提取关键参数（如相机型号、光圈值、焦距等），并将其作为文本水印添加到图像底部。
4. **logo水印添加**：支持在图像底部添加品牌logo或用户自定义logo。
5. **水印合成**：提供了经典白底水印和模糊背景水印两种合成方式，增强图像的版权保护和视觉效果。

## 三、安装与使用
### （一）安装依赖
项目依赖`rawpy`、`Pillow`、`exifread`、`PyYAML`等库。可通过以下命令安装：
```bash
pip install rawpy Pillow exifread PyYAML
```
### （二）配置文件
在项目根目录下的`config.yaml`文件中配置水印相关信息：
1. **logo**：设置logo的启用状态和品牌logo的路径。
2. **user**：配置摄影者信息。
3. **font**：指定用于文本水印的字体文件路径。
### （三）运行示例
在`if __name__ == "__main__":`代码块中，修改`raw_image_file`变量为实际的图像文件路径，然后运行脚本：
```python
if __name__ == "__main__":
    raw_image_file = "your_image_file.DNG"  # 替换为实际的图像文件名及路径
    iwm = ImageWaterMark(raw_image_file)
    print(iwm.__dict__)
    iwm.classic_watermark()
```
### （四）选择水印类型
1. **经典白底水印**：调用`classic_watermark`方法，将生成的水印图像垂直拼接在原始图像下方。
2. **模糊背景水印**：调用`blur_watermark`方法，对原始图像进行放大和高斯模糊处理，然后将原始图像粘贴到模糊后的图像上。

## 四、代码结构
1. **类定义**：`ImageWaterMark`类包含了图像读取、水印配置加载、水印生成、图像合成等一系列方法。
2. **属性定义**：包括字体大小字典`font_size_dict`、位置字典`position_dict`、logo字典`logo_dict`等，用于配置水印的样式和位置。
3. **方法说明**：
    - `get_image`：读取图像并转换为`Image`对象。
    - `load_config`：从`config.yaml`文件中读取配置信息。
    - `compute_aperture`：将光圈值字符串转换为精确的小数表示。
    - `watermark_font_size`：根据图像尺寸和水印类型计算合适的字体大小。
    - `watermark_position`：根据图像尺寸、水印类型和文本尺寸计算水印的位置。
    - `get_image_info`：读取图像的EXIF信息并提取关键参数，生成水印信息列表。
    - `genarate_watermark`：生成包含水印信息的图像。
    - `hconcat_images`和`vconcat_images`：分别实现图像的水平和垂直拼接。
    - `logo`：在图像上指定位置粘贴logo。
    - `resize_and_blur_image`：对图像进行放大和高斯模糊处理。
    - `paste_images`：将一个图像粘贴到另一个图像的指定位置。
    - `classic_watermark`和`blur_watermark`：分别生成经典白底水印和模糊背景水印。

## 五、注意事项
1. 确保`config.yaml`文件中的路径和配置信息正确无误。
2. 对于RAW格式文件，需要确保`rawpy`库支持该相机的RAW格式。
3. 水印字体文件路径需正确设置，否则可能导致字体加载失败。
4. 输出图像的格式和保存路径在代码中硬编码为`JPEG`格式和原文件名加上`_watermarked.jpg`后缀，如需修改，需手动调整代码。