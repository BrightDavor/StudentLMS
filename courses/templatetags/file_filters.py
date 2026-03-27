from django import template

register = template.Library()

@register.filter
def is_pdf(file_url):
    return str(file_url).lower().endswith('.pdf')

@register.filter
def is_video(file_url):
    return str(file_url).lower().endswith(('.mp4', '.mov', '.avi', '.mkv'))

@register.filter
def is_audio(file_url):
    return str(file_url).lower().endswith(('.mp3', '.wav', '.aac'))

@register.filter
def is_image(file_url):
    return str(file_url).lower().endswith(('.jpg', '.jpeg', '.png', '.gif'))
