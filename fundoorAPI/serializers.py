from rest_framework import serializers
from .models import *
import requests

# reading serializers
class NetworkReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Network
        fields = ['name', 'chainid']

class CategoryReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['name']

class UserReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['address']

class StatusReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Status
        fields = ['name']

class CurrencyReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Currency
        fields = ['address', 'name']

class MediaReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Media
        fields = ['id', 'project', 'image']

class ContributionReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contribution
        # fields = ['id', 'project', 'created_at', 'usd_amount', 'user', 'currency', 'amount', 'hsh']
        fields = ['created_at', 'usd_amount', 'user', 'currency', 'amount', 'hsh']
        depth = 1

class CommunityProposalReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = CommunityProposal
        fields = ['id', 'project', 'created_at', 'status', 'title', 'description', 'onchain_proposal_nonce']

class CommentReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['id', 'details', 'user', 'created_at']
        depth = 1

class ProjectReadSerializer(serializers.ModelSerializer):
    fundraiser = UserReadSerializer()
    currencies = CurrencyReadSerializer(many=True, read_only=True, source='currency.all')
    category = CategoryReadSerializer()
    status = StatusReadSerializer()
    media = MediaReadSerializer(many=True, read_only=True)
    contribution = ContributionReadSerializer(many=True, read_only=True, source='contribution_set')
    community_proposals = CommunityProposalReadSerializer(many=True, read_only=True, source='communityproposal_set')
    comments = CommentReadSerializer(many=True, read_only=True, source='comment_set')

    class Meta:
        model = Project
        fields = [
            'id',
            'fundraiser',
            'title',
            'description',
            'currencies',
            'category',
            'status',
            'project_address',
            'community_oversight',
            'created_at',
            'release_epoch',
            'creation_hash',
            'media', # FK
            'contribution', # FK
            'community_proposals', # FK
            'comments', # FK
        ]

# writing serializers
class MediaWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Media
        fields = ['project', 'image']

class ProjectWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ['fundraiser', 'title', 'description', 'currency', 'category', 'status', 'project_address', 'community_oversight',  'created_at', 'release_epoch', 'creation_hash']

class ContributionWriteSerializer(serializers.ModelSerializer):
    contributor = serializers.CharField(write_only=True)
    currencyAddress = serializers.CharField(write_only=True)

    class Meta:
        model = Contribution
        fields = ['contributor', 'currencyAddress', 'amount', 'hsh']

    # override to retrieve
    def create(self, validated_data):
        contributor = validated_data['contributor']
        currencyAddress = validated_data['currencyAddress']
        amount = validated_data['amount']
        hsh = validated_data['hsh']

        user = User.objects.get(address=contributor)
        currency = Currency.objects.get(address=currencyAddress)

        # Fetch USD amount using external API (Coinbase)
        if currency.name == 'WETH':
            response = requests.get(f"https://api.coinbase.com/v2/exchange-rates?currency=ETH")
        else:
            response = requests.get(f"https://api.coinbase.com/v2/exchange-rates?currency={currency.name}")
        if response.status_code == 200:
            usd_rate = response.json().get('data', {}).get('rates', {}).get('USD')
            usd_amount = float(usd_rate) * float(amount)
        else:
            usd_amount = 0

        contribution = Contribution.objects.create(
            project=self.context['project'],
            usd_amount=usd_amount,
            user=user,
            currency=currency,
            amount=amount,
            hsh=hsh
        )

        return contribution

class CommentWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['project', 'details', 'user']