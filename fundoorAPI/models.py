from django.db import models

class Network(models.Model):
    # network deployed
    name = models.CharField(null=False, blank=False, max_length=100)
    # chain id
    chainid = models.IntegerField(null=False, blank=False)
    def __str__(self):
        return self.name

class Category(models.Model):
    # category names
    name = models.CharField(null=False, blank=False, max_length=100)
    def __str__(self):
        return self.name

class User(models.Model):
    # user address
    address = models.CharField(null=False, blank=False, default="0x", max_length=42)
    def __str__(self):
            return self.address

class Status(models.Model):
    # status names (Active / Inactive / Blocked etc)
    name = models.CharField(null=False, blank=False, max_length=100)
    def __str__(self):
        return self.name

class Currency(models.Model):
    # address
    address = models.CharField(null=False, blank=False, default="0x", max_length=42)
    # network
    network = models.ForeignKey(Network, on_delete=models.PROTECT)
    # name
    name = models.CharField(null=False, blank=False, default="ERC20", max_length=100)

class Project(models.Model):
    # fundraiser of the project
    fundraiser = models.ForeignKey(User, on_delete=models.PROTECT)
    # title of the project
    title = models.CharField(max_length=100)
    # description of the project
    description = models.TextField(null=True)
    # category of the project
    currency = models.ManyToManyField(Currency)
    # category of the project
    category = models.ForeignKey(Category, on_delete=models.PROTECT)
    # status of the project
    status = models.ForeignKey(Status, on_delete=models.PROTECT)
    # project address
    project_address = models.CharField(max_length=42)
    # community oversight
    community_oversight = models.BooleanField(default=False)
    # project creation time
    created_at = models.DateTimeField(auto_now_add=True)
    # project release epoch
    release_epoch = models.IntegerField()
    # The project creation transaction hash
    creation_hash = models.CharField(max_length=66, null=False, blank=False, default="0x")

class Media(models.Model):
    # linking to project
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    # photo
    image = models.ImageField(upload_to='user_upload/', null=True)

class Contribution(models.Model):
    # project
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    # timestamp
    created_at = models.DateTimeField(auto_now_add=True)
    # usd_amount
    usd_amount = models.DecimalField(max_digits=12, decimal_places=2)
    # user
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    # currency
    currency = models.ForeignKey(Currency, on_delete=models.CASCADE)
    # amount
    amount = models.DecimalField(max_digits=80, decimal_places=18)
    # transaction hash
    hsh = models.CharField(null=False, blank=False, default="0x", max_length=100)

class CommunityProposal(models.Model):
    # link to project
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    # timestamp
    created_at = models.DateTimeField(auto_now_add=True)
    # status
    status = models.ForeignKey(Status, on_delete=models.PROTECT)
    # title
    title = models.CharField(null=False, blank=False, max_length=100)
    # description
    description = models.TextField(null=True, blank=True)
    # proposal nonce
    onchain_proposal_nonce = models.IntegerField(null=False, blank=False)

class Comment(models.Model):
    # link to project
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    # description
    details = models.TextField(null=True, blank=True)
    # user
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    # initiation time
    created_at = models.DateTimeField(auto_now_add=True)