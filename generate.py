from PIL import Image, ImageDraw, ImageFont
import random

def postcard(name):
    a = random.randint(0, 5)
    img = Image.open(f'media/{a}.jpg')
    text_postcard = 'Поздравляю тебя\nс новым годом, '
    if len(name) >= 8:
        text_postcard += "\n" + name
    else:
        text_postcard += name
    if a == 0:
        font = ImageFont.truetype("arial.ttf", size=100)
        draw = ImageDraw.Draw(img)
        draw.text((300, 600), text_postcard, font=font)
        img.save('test/postcard.jpg')
        img = Image.open('test/postcard.jpg')
        return img
    elif a == 1:
        font = ImageFont.truetype("arial.ttf", size=20)
        draw = ImageDraw.Draw(img)
        draw.text((150, 40), text_postcard, "blue",font=font)
        img.save('test/postcard.jpg')
        img = Image.open('test/postcard.jpg')
        return img
    elif a == 2:
        font = ImageFont.truetype("arial.ttf", size=100)
        draw = ImageDraw.Draw(img)
        draw.text((300, 800), text_postcard, "green", font=font)
        img.save('test/postcard.jpg')
        img = Image.open('test/postcard.jpg')
        return img
    elif a == 3:
        font = ImageFont.truetype("arial.ttf", size=100)
        draw = ImageDraw.Draw(img)
        draw.text((300, 800), text_postcard, "green", font=font)
        img.save('test/postcard.jpg')
        img = Image.open('test/postcard.jpg')
        return img
    elif a == 4:
        font = ImageFont.truetype("arial.ttf", size=100)
        draw = ImageDraw.Draw(img)
        draw.text((300, 700), text_postcard, font=font)
        img.save('test/postcard.jpg')
        img = Image.open('test/postcard.jpg')
        return img
    else:
        font = ImageFont.truetype("arial.ttf", size=100)
        draw = ImageDraw.Draw(img)
        draw.text((70, 400), text_postcard, font=font)
        img.save('test/postcard.jpg')
        img = Image.open('test/postcard.jpg')
        return img
