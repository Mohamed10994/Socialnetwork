from django.shortcuts import render, redirect
from django.views import View
from .models import Post, Comment, UserProfile,Notification, ThreadModel, MessageModel, Image, Tag
from .forms import PostForm, CommentForm, ThreadForm, MessageForm, SharedForm, ExploreForm
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from django.views.generic.edit import UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from django.http import HttpResponseRedirect, HttpResponse
from django.db.models import Q, Count
from django.contrib import messages
from django.utils import timezone
from django.shortcuts import get_object_or_404



class PostListView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        form = PostForm()
        share_form = SharedForm()
        profile_list = UserProfile.objects.all()[:5]
        post_list = Post.objects.get_following_posts(
            user = request.user
        )
        most_popular_posts = Post.objects.annotate(
            num_comments=Count('comments')).order_by('-num_comments')[:10]
        
        context = {
            'post_list': post_list,
            'shareform': share_form,
            'form': form,
            'profile_list': profile_list,
            'most_popular_posts': most_popular_posts
        }
        return render(request, 'social/post_list.html', context)
    
    def post(self, request, *args, **kwargs):
        share_form = SharedForm()
        
        posts = Post.objects.get_following_posts(
            user = request.user
        )
        
        profile_list = UserProfile.objects.all()[:10]
        
        form = PostForm(request.POST, request.FILES)
        
        files = request.FILES.getlist('image')
        

        most_popular_posts = Post.objects.annotate(num_comments=Count('comments')).order_by('-num_comments')[:10]
        
        if form.is_valid():
            new_post = form.save(commit=False)
            new_post.assign_author(author=request.user)
            new_post.create_tags()
            
            for file in files:
                img = Image.objects.create(
                    image = file,
                )
                new_post.image.add(img)
                

        form = PostForm()
        
        context = {
            'post_list': posts,
            'shareform': share_form,
            'form': form,
            'profile_list': profile_list,
            'most_popular_posts':most_popular_posts,
        }
        
        return render(request, 'social/post_list.html', context)
    
class PostDetailView(LoginRequiredMixin, View):
    def get(self, request, pk, *args, **kwargs):
        form = CommentForm()
        
        post = get_object_or_404(Post, pk=pk)
        
        comments = Comment.objects.related_post(post=post)
        
        context = {
            'post': post,
            'form': form,
            'comments': comments,
        }
        return render(request, 'social/post_detail.html', context)
    
    def post(self, request, pk, *args, **kwargs):
        form = CommentForm(request.POST)
        
        post = get_object_or_404(Post, pk=pk)
 
        if form.is_valid():
            new_comment = form.save(commit=False)
            new_comment.save_data(
                author=request.user,
                post=post
            )
            new_comment.create_tags()
            
        comments = Comment.objects.related_post(post=post)
        
        Notification.objects.add_comment(
            form_user=request.user,
            to_user=post.author,
            post=post
        )
        
        context = {
            'post': post,
            'form': form,
            'comments': comments,
        }
        return render(request, 'social/post_detail.html', context)
    
class CommentReplyView(LoginRequiredMixin, View):
    def post(self, request, post_pk, pk, *args, **kwargs):
        form = CommentForm(request.POST)
        
        post = get_object_or_404(Post, pk=post_pk)
        
        parent_comment = get_object_or_404(Comment, pk=pk)

        if form.is_valid():
            new_comment = form.save(commit=False)
            new_comment.save_data(
                author=request.author,
                post=post,
                parent=parent_comment
            )

        Notification.objects.add_comment(
            form_user=request.user,
            to_user=parent_comment.author,
            comment=new_comment
        )
        return redirect('social:post-detail', pk=post_pk)
 
class PostEditView(LoginRequiredMixin, UserPassesTestMixin ,UpdateView):
    model = Post
    fields = ['body']
    template_name = 'social/post_edit.html'
    
    def get_success_url(self):
        pk = self.kwargs['pk']
        return reverse_lazy('social:post-detail', kwargs={'pk': pk})
    def test_func(self):
        post = self.get_object()
        return self.request.user == post.author

class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Post
    template_name = 'social/post_delete.html'
    success_url = reverse_lazy('social:post-list')
    
    def test_func(self):
        post = self.get_object()
        return self.request.user == post.author
    
class SharedPostView(View):
    def post(self, request, pk, *args, **kwargs):
        form = SharedForm(request.POST)
        
        original_post = Post.objects.get(pk=pk)
        
        if form.is_valid():
            new_post = Post.objects.create(
                shared_body = self.request.POST.get('body'),
                body = original_post.body,
                author = original_post.author,
                created_on = original_post.created_on,
                shared_user = request.user,
                shared_on = timezone.now(),
            )
            
            new_post.image.add(*original_post.image.all())
        return redirect('social:post-list')
    

class CommentDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Comment
    template_name = 'social/comment_delete.html'
    
    def get_success_url(self):
        pk = self.kwargs['post_pk']
        return reverse_lazy('social:post-detail', kwargs={'pk': pk})
    def test_func(self):
        comment = self.get_object()
        return self.request.user == comment.author
    
class AddCommentLikes(LoginRequiredMixin, View):
    def post(self, request, pk, *args, **kwargs):
        comment = get_object_or_404(Comment, pk=pk)
        
        if comment.likes.filter(pk=request.user.pk).exists():
            comment.likes.remove(request.user)
        else:
            Notification.objects.add_like(
                form_user=request.user,
                to_user=comment.author,
                comment=comment
            )
            comment.likes.add(request.user)

        next = request.POST.get('next', '/  ')
        return HttpResponseRedirect(next)

    
class ProfileView(View):
    def get(self, request, pk, *args, **kwargs):
        profile = get_object_or_404(UserProfile, pk=pk)

        posts = Post.objects.filter(author=profile.user).order_by('-created_on')
        
        images = Post.objects.filter(author=profile.user).order_by('-created_on')[:3]
        
        followers = profile.followers.values(
            'profile__pk',
            'username',
            'profile__picture',
        )
        
        is_following = profile.followers.filter(pk=request.user.pk).exists()

        number_of_followers = followers.count()
        
        context = {
            'profile': profile, 
            'posts': posts,
            'is_following': is_following,
            'number_of_followers': number_of_followers,
            'followers': followers,
            'images': images
        }
        return render(request, 'social/profile.html', context)
        
class ProfileEditView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = UserProfile
    fields = ['name', 'bio', 'birth_date', 'location', 'picture']
    template_name = 'social/profile_edit.html'
    
    def get_success_url(self):
        pk = self.kwargs['pk']
        return reverse_lazy('social:profile', kwargs={'pk': pk})
    def test_func(self):
        return self.request.user == self.get_object().user

class AddFollower(LoginRequiredMixin, View):
    def post(self, request, pk, *args, **kwargs):
        profile = get_object_or_404(UserProfile, pk=pk)
        
        profile.followers.add(request.user)
        
        Notification.objects.add_follow(
            form_user=request.user,
            to_user=profile.user
        )
        
        return redirect('social:profile', pk=pk)

class RemoveFollower(LoginRequiredMixin, View):
    def post(self,request, pk, *args, **kwargs):
        profile = get_object_or_404(UserProfile, pk=pk)
        
        profile.followers.remove(request.user)
        
        return redirect('social:profile', pk=profile.pk)
    
class ListFollowers(View):
    def get(self, request, pk, *args, **kwargs):
        profile = UserProfile.objects.get(pk=pk)
        followers = profile.followers.all()
        
        context = {
            'profile': profile,
            'followers': followers,
        }
        return render(request, 'social/followers_list.html', context)
    
class AddLike(LoginRequiredMixin, View):
    def post(self, request, pk, *args, **kwargs):
        post = Post.objects.get(pk=pk)
        
        if post.likes.filter(pk=request.user.pk).exists():
            post.likes.remove(request.user)
        else:
            Notification.objects.add_like(
                form_user=request.user,
                to_user=post.author,
                post=post
            )
            post.likes.add(request.user)

        next = request.POST.get('next', '/social')
        
        return HttpResponseRedirect(next)
            
    
class UserSearch(View):
    def get(self,request, *args, **kwargs):
        query = self.request.GET.get('query', '')
        profile_list = UserProfile.objects.search(query=query)
        
        context = {
            'profile_list': profile_list,
        }
        return render(request, 'social/search.html', context)
    
class PostNotification(View):
    def get(self, request, notification_pk, post_pk, *args, **kwargs):

        Notification.objects.filter(
            pk=notification_pk
        ).update(
            user_has_seen=True
        )
        
        return redirect('social:post-detail', pk=post_pk)
    
class FollowNotification(View):
    def get(self, request, notification_pk, profile_pk, *args, **kwargs):
        Notification.objects.filter(
            pk=notification_pk
        ).update(
            user_has_seen=True
        )
        
        return redirect('social:profile', pk=profile_pk)
    
class ThreadNotification(View):
    def get(self, request,notification_pk, object_k, *args, **kwargs):
        Notification.objects.filter(
            pk=notification_pk
        ).update(
            user_has_seen=True
        )
        return redirect('social:thread', pk=object_k) 
    
class RemoveNotification(View):
    def delete(self, request, notification_pk, *args, **kwargs):
        Notification.objects.filter(
            pk=notification_pk
        ).update(
            user_has_seen=True
        )
        return HttpResponse('Success', content_type='text/plain')
 
# Searching for user 
class CreateThread(View):
    # Will display the form to enter a username
    def get(self, request, *args, **kwargs):
        form = ThreadForm()
        context = {
            'form': form,
        }
        return render(request, 'social/create_thread.html', context)
    # Handle creating the thread 
    def post(self, request, *args, **kwargs):
        form = ThreadForm(request.POST)
        username = request.POST.get('username')
        
        try:
            receiver = User.objects.get(username=username)
            if ThreadModel.objects.filter(user=request.user, receiver=receiver).exists():   
                thread = ThreadModel.objects.filter(user=request.user, receiver=receiver)[0]
                return redirect('social:thread', pk=thread.pk)
            if form.is_valid():
                sender_thread = ThreadModel(
                    user=request.user,
                    receiver=receiver,
                )
                sender_thread.save()
                thread_pk = sender_thread.pk
                return redirect('social:thread', pk=thread_pk)
        except:
            messages.error(request, 'User not found.')
            return redirect('social:create-thread')
    
# Our inbox to see all of our conversations
class ListThreads(View):
    def get(self, request, *args, **kwargs):
        threads = ThreadModel.objects.filter(Q(user=request.user) | Q(receiver=request.user))
        context = {
            'threads': threads,
        }
        return render(request, 'social/inbox.html', context)

# For create the message   
class CreateMessage(View):
    def post(self, request, pk, *args, **kwargs):
        form = MessageForm(request.POST, request.FILES)
        thread = ThreadModel.objects.get(pk=pk)
        if thread.receiver == request.user:
            receiver = thread.user
        else:
            receiver = thread.receiver
        
        if form.is_valid():
            message = form.save(commit=False)
            message.thread = thread
            message.sender_user = request.user
            message.receiver_user = receiver
            message.save()
            
            Notification.objects.add_dm(
            form_user=request.user,
            to_user = receiver, 
            thread=thread,
        )
        
        return redirect('social:thread', pk=pk)
    
# For display all the messages
class ThreadView(View):
    def get(self, request, pk, *args, **kwargs):
        form_thread = ThreadForm()
        form = MessageForm()
        thread =  ThreadModel.objects.get(pk=pk)
        message_list = MessageModel.objects.filter(thread__pk__contains=pk)
        threads = ThreadModel.objects.filter(Q(user=request.user) | Q(receiver=request.user))
        context = {
            'thread': thread,
            'form': form,
            'form_thread': form_thread,
            'message_list': message_list,
            'threads': threads
        }
        return render(request, 'social/thread.html', context)
    def post(self, request, *args, **kwargs):
        form = ThreadForm(request.POST)
        username = request.POST.get('username')
        
        try:
            receiver = User.objects.get(username=username)
            if ThreadModel.objects.filter(user=request.user, receiver=receiver).exists():   
                thread = ThreadModel.objects.filter(user=request.user, receiver=receiver)[0]
                return redirect('social:thread', pk=thread.pk)
            if form.is_valid():
                sender_thread = ThreadModel(
                    user=request.user,
                    receiver=receiver,
                )
                sender_thread.save()
                thread_pk = sender_thread.pk
                return redirect('social:thread', pk=thread_pk)
        except:
            messages.error(request, 'User not found.')
            return redirect('social:create-thread')
    
    
class Explore(View):
    def get(self, request, *args, **kwargs):
        explore_form =ExploreForm()
        query = self.request.GET.get('query')
        tag = Tag.objects.filter(name=query).first()
        share_form = SharedForm()
        if tag:
            posts = Post.objects.filter(tags__in=[tag])
        else:
            posts = Post.objects.all()
        
        context = {
            'tag': tag,
            'posts': posts,
            'shareform': share_form,
            'explore_form': explore_form
        }
        return render(request, 'social/explore.html', context)
    def post(self, request, *args, **kwargs):
        explore_form = ExploreForm(request.POST)
        share_form = SharedForm()
        if explore_form.is_valid():
            query = explore_form.cleaned_data['query']
            tag = Tag.objects.filter(name=query).first()
            posts = None
            if tag:
                posts = Post.objects.filter(tags__in=[tag])
            if posts:
                context = {
                    'tag': tag,
                    'shareform': share_form,
                    'posts': posts
                }
            else:
                context = {
                    'tag': tag,
                    'shareform': share_form,
                }
            return HttpResponseRedirect(f'/social/explore?query={query}')
        return HttpResponseRedirect('/social/explore/', context)
        