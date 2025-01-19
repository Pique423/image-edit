import rawpy
from PIL import Image, ImageDraw, ImageFont,ImageFilter
import exifread
import os
from decimal import Decimal, ROUND_HALF_UP
import yaml

font_size_dict={'model':50,'fas':100,'lens':100,'camera_brand':30,'author':40}
position_dict={'model':(0.03,0.3),'fas':(0.8,0.3),'lens':(0.8,0.4),'camera_brand':(0.6,0.4),'author':(0.03,0.5)}
logo_dict={'user_logo':10,'brand':0}
def load_config():
    with open('config.yaml', 'r',encoding='utf-8') as f:
        config = yaml.safe_load(f)
    # 读取输入、输出配置
    logo_enable = config['logo']['enable']
    brand = config['logo']['brand']
    # 读取摄影者信息配置
    user = config['user']
    font = config['font']
    return {'logo_enable':logo_enable,'brand':brand,'user':user,'font':font}

user_config=load_config()
def compute_aperture(aperture_str):
    aperture=0
    if '/' in aperture_str:
        apertures = aperture_str.split('/')
        aperture = float(apertures[0])/ float(apertures[1])
    else :
        aperture=float(aperture_str)
    num = Decimal(aperture)
    rounded_num = num.quantize(Decimal('0.00'), rounding=ROUND_HALF_UP)
    return str(rounded_num).rstrip('0').rstrip('.') if '.' in str(rounded_num) else str(rounded_num)

def get_raw(image_path):
    image=Image.new('RGB', (1, 1), (255, 255, 255))
    try:
        with rawpy.imread(image_path) as raw:
            rgb_image = raw.postprocess()
            image = Image.fromarray(rgb_image)
    except rawpy._rawpy.LibRawFileUnsupportedError as libRawFileUnsupportedError:
        image = Image.open(image_path)
    return image

def get_image_info(image_path):
    with open(image_path, 'rb') as f:
        tags = exifread.process_file(f)
    return {'model':str(tags.get('Image Model', '')).replace("'", ""),
    'aperture' : compute_aperture(str(tags.get('EXIF FNumber', '')).replace("'", "")),
    'focal_length' : str(tags.get('EXIF FocalLengthIn35mmFilm', '')).replace("'", ""),
    'shutter_speed' : str(tags.get('EXIF ExposureTime', '')).replace("'", ""),
    'iso' : str(tags.get('EXIF ISOSpeedRatings', '')).replace("'", ""),
    'lens' : str(tags.get('EXIF LensModel', '')).replace("'", ""),
    'camera_brand':str(tags.get('Image Make','')).replace("'", "")}

def watermark_font_size(info_type,width, height):
    return int(min(width, height) / font_size_dict[info_type])

def watermark_position(info_type,width,text_width,bottom_area_height,text_height,):
    position=(0,0)
    if info_type =='model':
        position=(width*position_dict['model'][0],int(bottom_area_height*position_dict['model'][1]))
    elif info_type =='fas':
        position=(int(width*position_dict['fas'][0]),int(bottom_area_height*position_dict['fas'][1]))
    elif info_type =='lens':
        position=(int(width*position_dict['lens'][0]),int(bottom_area_height*position_dict['lens'][1])+text_height)
    elif info_type=='camera_brand':
        #position=(int(width*position_dict['camera_brand'][0]),int(bottom_area_height*position_dict['camera_brand'][1]))
        pass
    else:
        position=(int(width*position_dict['author'][0]),int(bottom_area_height*position_dict['author'][1]))
    return position

def hconcat_images(image1, image2):
    width1, height1 = image1.size
    width2, height2 = image2.size
    new_width = width1 + width2
    new_height = max(height1, height2)
    new_image = Image.new('RGB', (new_width, new_height))
    new_image.paste(image1, (0, 0))
    new_image.paste(image2, (width1, 0))
    return new_image

def vconcat_images(image1, image2):
    width1, height1 = image1.size
    width2, height2 = image2.size
    new_width = max(width1, width2)
    new_height = height1 + height2
    new_image = Image.new('RGB', (new_width, new_height))
    new_image.paste(image1, (0, 0))
    new_image.paste(image2, (0, height1))
    return new_image

def genarate_watermark(width, height,watermarks,logo_file="logo.png"):
 # 字体文件路径（根据实际情况修改）
    # 确定白色底部区域的高度（可根据需要调整）
    bottom_area_height = int(height / 6.41)
    # 创建一个新的图像，底部为白色区域，其余部分为原始图像
    new_image = Image.new('RGB', (width, bottom_area_height), (255, 255, 255))
    # 创建绘制对象
    draw = ImageDraw.Draw(new_image)
    for watermark in watermarks:
        if watermark['model']=='camera_brand':
            logo(new_image,width,bottom_area_height,watermark['text'].lower())
        else:
            text = watermark['text']
            font_size = watermark['font_size']
            font = ImageFont.truetype(watermark['font_path'], font_size)
            text_color = (0, 0, 0)
            text_width, text_height = draw.textbbox((0,0),text,font=font)[2:]
            position=watermark_position(watermark['model'],width,text_width,bottom_area_height,text_height)
            draw.text(position, text, font=font, fill=text_color)
    logo(new_image,width,bottom_area_height,'user_logo')
    return new_image


def logo(new_image,width,bottom_area_height,logo_type):
    logo = Image.open(user_config['brand'][logo_type]['path'])
    logo.thumbnail((width // 4, bottom_area_height/4), Image.Resampling.BICUBIC)
    x_logo = int(width*(0.65 if logo_type=='user_logo' else 0.6))
    y_logo = int(bottom_area_height*0.4)
    new_image.paste(logo, (x_logo, y_logo))


def resize_and_blur_image(img):
    # 获取图片的宽度和高度
    width, height = img.size
    # 计算放大10%后的尺寸
    new_width = int(width * 1.1)
    new_height = int(height * 1.2)
    # 放大图片
    resized_img = img.resize((new_width, new_height), Image.LANCZOS)
    return resized_img.filter(ImageFilter.GaussianBlur(radius=100))
def paste_images(image1,image2):
    width1,height1 = image1.size
    width2,height2 = image2.size
    x=(width1-width2)//2
    y=(height1-height2)//3
    image1.paste(image2,(x,y))
    return image1
def add_sony_a7m4_watermark(image_path):
    # 使用rawpy将RAW格式转换为可处理的RGB图像格式（通过PIL的Image表示）
    image=get_raw(image_path)

    # 获取图像的宽度和高度，用于后续自适应调整水印大小和位置
    width, height = image.size

    # 读取EXIF信息获取机型、光圈、焦距、快门、ISO等参数
    image_info=get_image_info(image_path)
    watermarks = [
    {'model':'model','font_path':user_config['font']['model'],'text': image_info['model'], 'font_size': watermark_font_size('model',width, height)},
    {'model':'fas','font_path':user_config['font']['fas'],'text': f"{image_info['focal_length']}mm f{image_info['aperture']} {image_info['shutter_speed']}s ISO{image_info['iso']}", 'font_size':  watermark_font_size('fas',width, height)},
    {'model':'lens','font_path':user_config['font']['lens'],'text': image_info['lens'], 'font_size':  watermark_font_size('lens',width, height)},
    {'model':'camera_brand','text': image_info['camera_brand']},#+'  |  ', 'font_size':  watermark_font_size('camera_brand',width, height)}
    {'model':'author','font_path':user_config['font']['author'],'text': 'PoweredBY Whischick', 'font_size':  watermark_font_size('model',width, height)}
]
    # classic_watermark(image_path,image,width, height,watermarks)
    blur_image=resize_and_blur_image(image)
    pasted_images = paste_images(blur_image,image)
    pasted_images.show()
    pasted_images.save(os.path.splitext(image_path)[0] + "_watermarked.jpg")

def classic_watermark(image_path,image,width, height,watermarks):
    watermark_image = genarate_watermark(width, height,watermarks)
    # 打开logo图片并调整其大小（这里简单限制最大宽度为白色区域宽度的一半，可按需调整）
    new_image=vconcat_images(image,watermark_image)
    # 保存添加水印后的图像，这里以JPEG格式保存，可按需修改保存格式
    output_path = os.path.splitext(image_path)[0] + "_watermarked.jpg"
    new_image.save(output_path)

if __name__ == "__main__":

    #raw_image_file = "DSC00218.ARW"  # 替换为实际的RAW格式照片文件名及路径
    raw_image_file = "IMG_1861.DNG"  # 替换为实际的RAW格式照片文件名及路径
    add_sony_a7m4_watermark(raw_image_file)
