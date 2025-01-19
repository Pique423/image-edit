import rawpy
from PIL import Image, ImageDraw, ImageFont,ImageFilter
import exifread
import os
from decimal import Decimal, ROUND_HALF_UP
import yaml
class ImageWaterMark():
    font_size_dict={'model':50,'fas':100,'lens':100,'camera_brand':30,'author':40}
    position_dict={'model':(0.03,0.3),'fas':(0.8,0.3),'lens':(0.8,0.4),'camera_brand':(0.6,0.4),'author':(0.03,0.5)}
    logo_dict={'user_logo':10,'brand':0}

    def __init__(self,image_path):
        self.image_path=image_path
        self.image=self.get_image()
        self.user_config=self.load_config()
        self.width, self.height = self.image.size
        self.image_info=self.get_image_info()
        self.bottom_area_height=int(self.height / 6.41)
    # 读取图像并转换为PIL的Image对象，若格式不支持则直接打开图像
    def get_image(self):
        image=Image.new('RGB', (1, 1), (255, 255, 255))
        try:
            with rawpy.imread(self.image_path) as raw:
                rgb_image = raw.postprocess()
                image = Image.fromarray(rgb_image)
        except rawpy._rawpy.LibRawFileUnsupportedError as libRawFileUnsupportedError:
            image = Image.open(self.image_path)
        return image
    # 从config.yaml文件中读取配置信息
    def load_config(self):
        with open('config.yaml', 'r',encoding='utf-8') as f:
            config = yaml.safe_load(f)
        # 读取输入、输出配置
        logo_enable = config['logo']['enable']
        brand = config['logo']['brand']
        # 读取摄影者信息配置
        user = config['user']
        font = config['font']
        return {'logo_enable':logo_enable,'brand':brand,'user':user,'font':font}
    # 将光圈值字符串转换为精确的小数表示
    def compute_aperture(slef,aperture_str):
        aperture=0
        if '/' in aperture_str:
            apertures = aperture_str.split('/')
            aperture = float(apertures[0])/ float(apertures[1])
        else :
            aperture=float(aperture_str)
        num = Decimal(aperture)
        rounded_num = num.quantize(Decimal('0.00'), rounding=ROUND_HALF_UP)
        return str(rounded_num).rstrip('0').rstrip('.') if '.' in str(rounded_num) else str(rounded_num)
    # 根据图像尺寸和水印类型计算合适的字体大小
    def watermark_font_size(self,info_type):
        return int(min(self.width,self.height) / self.font_size_dict[info_type])
    # 根据图像尺寸、水印类型和文本尺寸计算水印的位置
    def watermark_position(self,info_type,text_width,text_height):
        position=(0,0)
        if info_type =='model':
            position=(self.width*self.position_dict['model'][0],int(self.bottom_area_height*self.position_dict['model'][1]))
        elif info_type =='fas':
            position=(int(self.width*self.position_dict['fas'][0]),int(self.bottom_area_height*self.position_dict['fas'][1]))
        elif info_type =='lens':
            position=(int(self.width*self.position_dict['lens'][0]),int(self.bottom_area_height*self.position_dict['lens'][1])+text_height)
        elif info_type=='camera_brand':
            #position=(int(width*position_dict['camera_brand'][0]),int(self.bottom_area_height*position_dict['camera_brand'][1]))
            pass
        else:
            position=(int(self.width*self.position_dict['author'][0]),int(self.bottom_area_height*self.position_dict['author'][1]))
        return position
    # 读取图像的EXIF信息并提取关键参数
    def get_image_info(self):
        with open(self.image_path, 'rb') as f:
            tags = exifread.process_file(f)
        image_info= {'model':str(tags.get('Image Model', '')).replace("'", ""),
        'aperture' : self.compute_aperture(str(tags.get('EXIF FNumber', '')).replace("'", "")),
        'focal_length' : str(tags.get('EXIF FocalLengthIn35mmFilm', '')).replace("'", ""),
        'shutter_speed' : str(tags.get('EXIF ExposureTime', '')).replace("'", ""),
        'iso' : str(tags.get('EXIF ISOSpeedRatings', '')).replace("'", ""),
        'lens' : str(tags.get('EXIF LensModel', '')).replace("'", ""),
        'camera_brand':str(tags.get('Image Make','')).replace("'", "")}
        watermarks = [
        {'model':'model','font_path':self.user_config['font']['model'],'text': image_info['model'], 'font_size': self.watermark_font_size('model')},
        {'model':'fas','font_path':self.user_config['font']['fas'],'text': f"{image_info['focal_length']}mm f{image_info['aperture']} {image_info['shutter_speed']}s ISO{image_info['iso']}", 'font_size':  self.watermark_font_size('fas')},
        {'model':'lens','font_path':self.user_config['font']['lens'],'text': image_info['lens'], 'font_size':  self.watermark_font_size('lens')},
        {'model':'camera_brand','text': image_info['camera_brand']},#+'  |  ', 'font_size':  watermark_font_size('camera_brand',width, height)}
        {'model':'author','font_path':self.user_config['font']['author'],'text': 'PoweredBY Whischick', 'font_size': self.watermark_font_size('model')}]
        return watermarks
    #生成包含水印信息的图像，支持添加文本水印和logo-经典水印
    def genarate_watermark(self,watermarks):
     # 字体文件路径（根据实际情况修改）
        # 确定白色底部区域的高度（可根据需要调整）
        # 创建一个新的图像，底部为白色区域，其余部分为原始图像
        new_image = Image.new('RGB', (self.width, self.bottom_area_height), (255, 255, 255))
        # 创建绘制对象
        draw = ImageDraw.Draw(new_image)
        for watermark in watermarks:
            if watermark['model']=='camera_brand':
                self.logo(new_image,watermark['text'].lower())
            else:
                text = watermark['text']
                font_size = watermark['font_size']
                font = ImageFont.truetype(watermark['font_path'], font_size)
                text_color = (0, 0, 0)
                text_width, text_height = draw.textbbox((0,0),text,font=font)[2:]
                position=self.watermark_position(watermark['model'],text_width,text_height)
                draw.text(position, text, font=font, fill=text_color)
        self.logo(new_image,'user_logo')
        return new_image
    #合成照片-水平拼接
    def hconcat_images(self,image1):
        width1, height1 = image1.size
        new_width = width1 + self.width
        new_height = max(height1, self.height)
        new_image = Image.new('RGB', (new_width, new_height))
        new_image.paste(self.image, (0, 0))
        new_image.paste(image1, (self.width, 0))
        return new_image
    #合成照片-垂直拼接
    def vconcat_images(self,image1):
        width1, height1 = image1.size
        new_width = max(width1, self.width)
        new_height = height1 + self.height
        new_image = Image.new('RGB', (new_width, new_height))
        new_image.paste(self.image, (0, 0))
        new_image.paste(image1, (0, self.height))
        return new_image
    #在图像上指定位置粘贴logo
    def logo(self,new_image,logo_type):
        logo = Image.open(self.user_config['brand'][logo_type]['path'])
        logo.thumbnail((self.width // 4, self.bottom_area_height/4), Image.Resampling.BICUBIC)
        x_logo = int(self.width*(0.65 if logo_type=='user_logo' else 0.6))
        y_logo = int(self.bottom_area_height*0.4)
        new_image.paste(logo, (x_logo, y_logo))
    #对图像进行放大和高斯模糊处理-模糊背景生成
    def resize_and_blur_image(self):
        # 获取图片的宽度和高度
        width, height = self.image.size
        # 计算放大10%后的尺寸
        new_width = int(width * 1.1)
        new_height = int(height * 1.2)
        # 放大图片
        resized_img = self.image.resize((new_width, new_height), Image.LANCZOS)
        return resized_img.filter(ImageFilter.GaussianBlur(radius=100))
    #合成照片-粘贴：将一个图像粘贴到另一个图像的指定位置
    def paste_images(self,image1):
        width1,height1 = image1.size
        x=(width1-self.width)//2
        y=(height1-self.height)//3
        image1.paste(self.image,(x,y))
        return image1
    
    #经典白底水印-将生成的水印图像垂直拼接在原始图像下方
    def classic_watermark(self):
        watermarks=self.get_image_info()
        watermark_image = self.genarate_watermark(watermarks)
        # 打开logo图片并调整其大小（这里简单限制最大宽度为白色区域宽度的一半，可按需调整）
        new_image=self.vconcat_images(watermark_image)
        # 保存添加水印后的图像，这里以JPEG格式保存，可按需修改保存格式
        output_path = os.path.splitext(self.image_path)[0] + "_watermarked.jpg"
        new_image.save(output_path)

    #模糊背景水印
    def blur_watermark(self):
        blur_image=self.resize_and_blur_image(self.image)
        pasted_images = self.paste_images(blur_image,self.image)
        pasted_images.save(os.path.splitext(self.image_path)[0] + "_watermarked.jpg")

if __name__ == "__main__":
    raw_image_file = "DSC08457.ARW"  # 替换为实际的RAW格式照片文件名及路径
    #raw_image_file = "IMG_1861.DNG"  # 替换为实际的RAW格式照片文件名及路径
    iwm=ImageWaterMark(raw_image_file)
    print(iwm.__dict__)
    iwm.classic_watermark()