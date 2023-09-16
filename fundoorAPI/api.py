# import DRF and FileResponse
from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework import status
from django.http import FileResponse
# Data operator
from django.db.models import Sum
from django.db.models.functions import Coalesce
# Import Decimal
from decimal import Decimal 
# import database models and serializers
from .models import *
from .serializers import *

# Creating API endpoints
@api_view(['POST'])
@parser_classes([MultiPartParser, FormParser])
def initiate_project(request):
    try:
        network, _ = Network.objects.get_or_create(
            name = request.data.get('chain', 'Optimism Goerli Testnet'), 
            chainid = request.data.get('chainid', 420)
            )
        currency, _ = Currency.objects.get_or_create(
            address = request.data.get('currency', ''),
            name = request.data.get('currencyName', 'ERC20'),
            network = network
            )
        category, _ = Category.objects.get_or_create(name=request.data.get('category'))
        fundraiser, _ = User.objects.get_or_create(address=request.data.get('walletAddress'))

        project_data = {
            'title': request.data.get('title', ''),
            'description': request.data.get('description', ''),
            'currency': [currency.id], 
            'category': category.id,
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
                media_serializer = MediaSerializer(data=media_data)
                if media_serializer.is_valid():
                    media_serializer.save()

            return Response(status=status.HTTP_200_OK)
        else:
            return Response({'errors': project_serializer.errors}, status=status.HTTP_400_BAD_REQUEST) 

    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

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

@api_view(['POST'])
def propose_community_action(request):
    project_address = request.data.get('projectAddress')
    if not project_address:
        return Response({'error': 'Project address not provided'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        project = Project.objects.get(project_address=project_address)
    except Project.DoesNotExist:
        return Response({'error': 'Project not found'}, status=status.HTTP_404_NOT_FOUND)

    project_data = {
        'project': project.id,
        'title': request.data.get('title', ''),
        'description': request.data.get('description', ''),
        'onchain_proposal_nonce': request.data.get('onchain_proposal_nonce', ''),
    }
    serializer = CommunityProposalWriteSerializer(data=project_data)

    if serializer.is_valid():
        serializer.save()
        return Response({'response': 1, 'message': 'Propose successful'}, status=status.HTTP_201_CREATED)
    else:
        return Response({'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def vote_community_action(request):
    try:
        voter = User.objects.get(address=request.data.get('user'))
    except User.DoesNotExist:
        return Response({'error': 'User is not a voter'}, status=status.HTTP_404_NOT_FOUND)

    vote_data = {
        'voter': voter.id,
        'proposal': request.data.get('proposal'),
        'weight': request.data.get('weight'),
        'vote': request.data.get('vote'),
        'hsh': request.data.get('hsh'),
    }
    
    # Deserialize the request data
    serializer = VoteWriteSerializer(data=vote_data)
    if serializer.is_valid():
        # Save the vote to the database
        serializer.save()

        # Respond with a success message
        return Response({'message': 'Vote recorded successfully'}, status=status.HTTP_201_CREATED)
    else:
        # Respond with validation errors
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Reading API endpoints
@api_view(['GET'])
def get_project_data(request, project_address):
    try:
        project = Project.objects.get(project_address=project_address)
        project_serializer = ProjectReadSerializer(instance=project, context={'request': request})

        return Response({"response": 1, "data": project_serializer.data}, status=status.HTTP_200_OK)
    except Project.DoesNotExist:
        return Response({'error': 'Project not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def get_community_proposals(request, project_address):
    try:
        project = Project.objects.get(project_address=project_address)
        # Filter community proposals based on the project address
        queryset = CommunityProposal.objects.filter(project=project.id)
        serializer = CommunityProposalReadSerializer(queryset, many=True)

        # Create the custom response
        custom_response = {
            "response": 1,
            "data": serializer.data
        }
        return Response(custom_response, status=status.HTTP_200_OK)

    except Project.DoesNotExist:
        return Response({'error': 'Project not found'}, status=status.HTTP_404_NOT_FOUND)
    except CommunityProposal.DoesNotExist:
        return Response({'error': 'No community proposals found for the given project address.'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def get_votes(request, proposal_id):
    try:
        # Query the database to get all votes for the given proposal_id
        votes = Vote.objects.filter(proposal=proposal_id)
        
        # Serialize the votes data
        serializer = VoteReadSerializer(votes, many=True)
        
        # Return the serialized data as a response
        return Response({"response": 1, "data": serializer.data}, status=status.HTTP_200_OK)
    
    except Vote.DoesNotExist:
        return Response({'error': 'No votes found for the given proposal ID.'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def search_projects(request):
    filter_field = request.query_params.get('field', None)
    filter_value = request.query_params.get('value', '')

    # Define a dictionary to map query parameters to model fields
    field_mapping = {
        'title': 'title__icontains',
        'category': 'category__name__icontains',
        'fundraiser': 'fundraiser__address',
        'contributor': 'contribution__user__address',
    }

    # Check if the specified field is valid
    if filter_field not in field_mapping:
        return Response({'error': 'Invalid filter field'}, status=status.HTTP_400_BAD_REQUEST)

    # Get the corresponding lookup field
    query = {field_mapping[filter_field]: filter_value}

    # Get the project set
    projects = Project.objects.filter(**query).distinct()

    # Serialize the filtered projects
    serializer = ProjectReadSerializer(projects, many=True, context={'request': request})

    return Response({"response": 1, "data": serializer.data}, status=status.HTTP_200_OK)


# Updating API endpoints
@api_view(['PUT'])
def update_comment(request, comment_id):
    try:
        comment = Comment.objects.get(pk=comment_id)
    except Comment.DoesNotExist:
        return Response({'error': 'Comment not found'}, status=status.HTTP_404_NOT_FOUND)

    serializer = CommentWriteSerializer(comment, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Deleting API endpoints
@api_view(['DELETE'])
def delete_comment(request, comment_id):
    try:
        comment = Comment.objects.get(pk=comment_id)
        comment.delete()
        return Response({'message': 'Comment deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
    except Comment.DoesNotExist:
        return Response({'error': 'Comment not found'}, status=status.HTTP_404_NOT_FOUND)
