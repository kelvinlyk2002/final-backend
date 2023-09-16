from django.urls import include, path
from . import views
from . import api

urlpatterns = [
    # static tests
    ## contribution history
    path('test1/', views.test1, name='test1'),
    ## project list
        # gallery - category project list
        # dashboard - my project- category project list
    path('test2/', views.test2, name='test2'),
    ## gallery - hero, trending, top projects
    path('test3/', views.test3, name='test3'),
    ## dashboard - updates from projects contributed
    path('test4/', views.test4, name='test4'),
    ## details
    path('test5/', views.test5, name='test5'),
    ## community action   - proposals for a project
    path('test6/', views.test6, name='test6'),
    ## deployed op details
    path('test7/', views.test7, name='test7'),
    ## initiate project
    path('api/initiate_project', api.initiate_project, name="initiate_project"),
    ## get project details
    path('api/get_project_data/<str:project_address>/', api.get_project_data, name='get_project_data'),
    ## get proposal details
    path('api/get_community_proposals/<str:project_address>/', api.get_community_proposals, name='get_community_proposals'),
    ## get voting details
    path('api/get_votes/<int:proposal_id>/', api.get_votes, name='get_votes'),
    ## contribute project
    path('api/contribute_project', api.contribute_project, name='contribute_project'),
    ## add currency to project
    path('api/add_currency', api.add_currency, name='add_currency'),
    ## add comment to project
    path('api/add_project_comment', api.add_project_comment, name='add_project_comment'),
    ## delete comment
    path('api/delete_comment/<str:comment_id>/', api.delete_comment, name='delete_comment'),
    ## update comment
    path('api/update_comment/<str:comment_id>/', api.update_comment, name='update_comment'),
    ## propose community action
    path('api/propose_community_action', api.propose_community_action, name='propose_community_action'),
    ## vote commmunity action
    path('api/vote_community_action', api.vote_community_action, name='vote_community_action'),
    ## search for a list of projects
    path('api/search_projects', api.search_projects, name='search_projects'),
    ## retrieve image by filename
    path('media/user_upload/<str:filename>', views.get_media, name='get_media'),
]