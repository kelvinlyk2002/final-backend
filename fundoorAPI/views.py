from django.shortcuts import render
from .models import *
from django.http import JsonResponse, FileResponse

# Create your views here.
def test1(request):
    return render(request, 'test1.html')

def test2(request):
    return render(request, 'test2.html')

def test3(request):
    return render(request, 'test3.html')

def test4(request):
    return render(request, 'test4.html')

def test5(request):
    return render(request, 'test5.html')

def test6(request):
    return render(request, 'test6.html')

def test7(request):
    return render(request, 'test7.html')

def get_media(request, filename):
    try:
        image_path = 'user_upload/' + filename

        # Find the media object by filename
        media = Media.objects.get(image=image_path)

        # Get the image
        image_file = media.image

        return FileResponse(image_file)
    except Media.DoesNotExist:
        return Response({'error': 'Image not found'}, status=404)