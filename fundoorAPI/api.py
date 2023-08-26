# import DRF
from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from django.http import JsonResponse
from rest_framework import status

# import database models and serializers
from .models import *
from .serializers import *

# reading API endpoints
@api_view(['GET'])
def get_project_data(request, project_address):
    try:
        project = Project.objects.get(project_address=project_address)
        project_serializer = ProjectReadSerializer(instance=project, context={'request': request})

        return Response({"response": 1, "data": project_serializer.data}, status=status.HTTP_200_OK)
    except Project.DoesNotExist:
        return JsonResponse({'error': 'Project not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


# writing API endpoints
@api_view(['POST'])
@parser_classes([MultiPartParser, FormParser])
def initiate_project(request):
    try:
        network, _ = Network.objects.get_or_create(
            name = request.data.get('chain', 'Optimism Goerli'), 
            chainid = request.data.get('chainid', 420)
            )
        currency, _ = Currency.objects.get_or_create(
            address = request.data.get('currency', ''),
            network = network
            )
        category, _ = Category.objects.get_or_create(name=request.data.get('category'))
        project_status, _ = Status.objects.get_or_create(name='active')
        fundraiser, _ = User.objects.get_or_create(address=request.data.get('walletAddress'))

        project_data = {
            'title': request.data.get('title', ''),
            'description': request.data.get('description', ''),
            'currency': [currency.id], 
            'category': category.id,
            'status': project_status.id,
            'project_address': request.data.get('projectAddress', ''),
            'community_oversight': request.data.get('communityOversight', False),
            'release_epoch': request.data.get('releaseEpoch', 0),
            'creation_hash': request.data.get('transactionHash', ''),
            'fundraiser': fundraiser.id,
        }
        
        project_serializer = ProjectWriteSerializer(data=project_data)
        if project_serializer.is_valid():
            # retain the project object to save the images
            project = project_serializer.save()

            images = request.FILES.getlist('images')

            for image in images:
                media_data = {'image': image, 'project': project.id}
                media_serializer = MediaWriteSerializer(data=media_data)
                if media_serializer.is_valid():
                    media_serializer.save()

            return Response(status=status.HTTP_200_OK)
        else:
            return JsonResponse({'errors': project_serializer.errors}, status=400) 

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@api_view(['POST'])
def contribute_project(request):
    try:
        project = Project.objects.get(project_address=request.data['projectAddress'])
    except Project.DoesNotExist:
        return Response({'error': 'Project not found'}, status=status.HTTP_404_NOT_FOUND)

    # context is required to allow access to the located project object 
    serializer = ContributionWriteSerializer(data=request.data, context={'project': project})
    if serializer.is_valid():
        serializer.save()
        return Response({'response': 1, 'message': 'Contribution successful'}, status=status.HTTP_201_CREATED)
    else:
        return Response({'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def add_currency(request):
    try:
        network, _ = Network.objects.get_or_create(
            name = request.data.get('chain', 'Optimism Goerli Testnet'), 
            chainid = request.data.get('chainid', 420)
            )
        currency, _ = Currency.objects.get_or_create(
            address = request.data.get('currencyAddress', ''),
            network = network
            )
        project = Project.objects.get(project_address=request.data['projectAddress'])
        project.currency.add(currency)

    except Project.DoesNotExist:
        return Response({'error': 'Project not found'}, status=status.HTTP_404_NOT_FOUND)
    
    return Response({'response': 1, 'message': 'Currency successfully added'}, status=status.HTTP_201_CREATED)

@api_view(['POST'])
def add_project_comment(request):
    project_address = request.data.get('projectAddress')
    if not project_address:
        return Response({'error': 'Project address not provided'}, status=status.HTTP_400_BAD_REQUEST)
    try:
        project = Project.objects.get(project_address=project_address)
    except Project.DoesNotExist:
        return Response({'error': 'Project not found'}, status=status.HTTP_404_NOT_FOUND)

    user_address = request.data.get('user')
    if not user_address:
        return Response({'error': 'User address not provided'}, status=status.HTTP_400_BAD_REQUEST)
    try:
        user = User.objects.get(address=user_address)
    except User.DoesNotExist:
        return Response({'error': 'User is not a fundraiser or contributor'}, status=status.HTTP_404_NOT_FOUND)

    details = request.data.get('details')
    if not details:
        return Response({'error': 'Empty comments not allowed'}, status=status.HTTP_400_BAD_REQUEST)

    serializer = CommentWriteSerializer(data={
        'project': project.id,
        'details': request.data['details'],
        'user': user.id
    })

    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
