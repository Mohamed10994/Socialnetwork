from django.urls import path
from .views import PostListView, PostDetailView, ProfileView, PostEditView, PostDeleteView, CommentDeleteView, ProfileEditView, AddFollower, RemoveFollower, AddLike, AddDislike, UserSearch, ListFollowers, AddCommentLikes, AddCommentDislike, CommentReplyView, PostNotification, FollowNotification, RemoveNotification, ListThreads, CreateThread, ThreadView, CreateMessage, SharedPostView

app_name = 'social'
 
urlpatterns = [
    path('', PostListView.as_view(), name='post-list'),
    path('post/<int:pk>/', PostDetailView.as_view(), name='post-detail'),
    path('post/edit/<int:pk>/', PostEditView.as_view(), name='post-edit'),
    path('post/delete/<int:pk>/', PostDeleteView.as_view(), name='post-delete'),
    path('post/<int:post_pk>/comment/delete/<int:pk>/', CommentDeleteView.as_view(), name='comment-delete'),
    path('post/<int:post_pk>/comment/<int:pk>/like', AddCommentLikes.as_view(), name='comment-like'),
    
    path('post/<int:pk>/like', AddLike.as_view(), name='like'),
    path('post/<int:post_pk>/comment/<int:pk>/like', AddCommentDislike.as_view(), name='comment-like'),
    
    path('post/<int:pk>/dislike', AddDislike.as_view(), name='dislike'),
    path('post/<int:post_pk>/comment/reply/<int:pk>', CommentReplyView.as_view(), name='comment-reply'),
    path('post/<int:pk>/share', SharedPostView.as_view(), name='share-post'),
    path('profile/<int:pk>/', ProfileView.as_view(), name='profile'),
    path('profile/edit/<int:pk>/', ProfileEditView.as_view(), name='profile-edit'),
    path('profile/<int:pk>/followers/add', AddFollower.as_view(), name='add-follower'),
    path('profile/<int:pk>/followers/remove', RemoveFollower.as_view(), name='remove-follower'),
    path('profile/<int:pk>/followers', ListFollowers.as_view(), name='followers-list'),
    path('search/', UserSearch.as_view(), name='profile-search'),
    path('notification/<int:notification_pk>/post/<int:object_pk>', PostNotification.as_view(), name='post-notification'),
    path('notification/<int:notification_pk>/follow/<int:object_pk>', FollowNotification.as_view(), name='follow-notification'),
    path('notification/delete/<int:notification_pk>', RemoveNotification.as_view(), name='notification-delete'),
    
    path('inbox/', ListThreads.as_view(), name='inbox'),
    
    path('inbox/create-thread', CreateThread.as_view(), name='create-thread'),
    
    path('inbox/<int:pk>/', ThreadView.as_view(), name='thread'),
    
    path('inbox/<int:pk>/create-message/', CreateMessage.as_view(), name='create-message'),
    
]