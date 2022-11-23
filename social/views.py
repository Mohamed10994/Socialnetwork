from django.shortcuts import render, redirect
from django.views import View
from .models import Post, Comment, UserProfile,Notification, ThreadModel, MessageModel, Image
from .forms import PostForm, CommentForm, ThreadForm, MessageForm, SharedForm
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from django.views.generic.edit import UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from django.http import HttpResponseRedirect, HttpResponse
from django.db.models import Q
from django.contrib import messages
from django.utils import timezone


class PostListView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        logged_in_user = request.user
        posts = Post.objects.filter(
            author__profile__followers__in=[logged_in_user.id]    
        )
        
        form = PostForm()
        share_form = SharedForm()
        
        context = {
            'post_list': posts,
            'shareform': share_form,
            'form': form,
        }
        return render(request, 'social/post_list.html', context)
    
    def post(self, request, *args, **kwargs):
        logged_in_user = request.user
        posts = Post.objects.filter(
            author__profile__followers__in=[logged_in_user.id]    
        )
        
        form = PostForm(request.POST, request.FILES)
        files = request.FILES.getlist('image')
        share_form = SharedForm()
        if form.is_valid():
            new_post = form.save(commit=False)
            new_post.author = request.user  
            new_post.save()
            
            for f in files:
                img = Image(image=f)
                img.save()
                new_post.image.add(img)
            new_post.save()
        
        context = {
            'post_list': posts,
            'shareform': share_form,
            'form': form,
        }
        
        return render(request, 'social/post_list.html', context)
    
class PostDetailView(LoginRequiredMixin, View):
    def get(self, request, pk, *args, **kwargs):
        post = Post.objects.get(pk=pk)
        form = CommentForm()
        
        comments = Comment.objects.filter(comment=post).order_by('-created_on')
        
        context = {
            'post': post,
            'form': form,
            'comments': comments,
        }
        return render(request, 'social/post_detail.html', context)
    
    def post(self, request, pk, *args, **kwargs):
        post = Post.objects.get(pk=pk)
        form = CommentForm(request.POST)
        
        if form.is_valid():
            new_comment = form.save(commit=False)
            new_comment.author = request.user
            new_comment.post = post
            new_comment.save()
            
        comments = Comment.objects.filter(comment=post).order_by('-created_on')
        notification = Notification.objects.create(notification_type=2, form_user=request.user, to_user=post.author, post=post)
        
        context = {
            'post': post,
            'form': form,
            'comment': comments,
        }
        return render(request, 'social/post_detail.html', context)
 
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
        original_post = Post.objects.get(pk=pk)
        form = SharedForm(request.POST)
        
        if form.is_valid():
            new_post = Post(
                shared_body = self.request.POST.get('body'),
                body = original_post.body,
                author = original_post.author,
                created_on = original_post.created_on,
                shared_user = request.user,
                shared_on = timezone.now(),
            )
            new_post.save()
            
            for img in original_post.image.all():
                new_post.image.add(img)
                
            new_post.save()
            
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
    def post(self, request, post_pk, pk, *args, **kwargs):
        comment = Comment.objects.get(pk=pk)
        
        is_dislike = False
        
        for dislike in comment.dislikes.all():
            if dislike == request.user:
                is_dislike = True
                break
        if is_dislike:
            comment.dislikes.remove(request.user)
        is_like = False
        
        for like in comment.like.all():
            if like == request.user:
                is_like = True
                break
        if not is_like:
            comment.likes.add(request.user)
            notification = Notification.objects.create(notification_type=1, form_user=request.user, to_user=comment.author, comment=comment)
        if is_like:
            comment.likes.remove(request.user)
        next = request.POST.get('next', '/social')
        return HttpResponseRedirect(next)

class AddCommentDislike(LoginRequiredMixin, View):
    def post(self, request, post_pk, pk, *args, **kwargs):
        comment = Comment.objects.get(pk=pk)
        is_like = False
        for like in comment.likes.all():
            if like == request.user:
                is_like = True
                break
        if is_like:
            comment.likes.remove(request.user)
        is_dislike = False
        for dislike in comment.dislikes.all():
            if dislike == request.user:
                is_dislike = True
                break
        if not is_dislike: 
            comment.dislikes.add(request.user)
        
        if is_dislike:
            comment.dislikes.remove(request.user)
        next = request.POST.get('next', '/social')
        return HttpResponseRedirect(next)
            
class CommentReplyView(LoginRequiredMixin, View):
    def post(self, request, post_pk, pk, *args, **kwargs):
        post = Post.objects.get(pk=post_pk)
        parent_comment = Comment.objects.get(pk=pk)
        form = CommentForm(request.POST)
        
        if form.is_valid():
            new_comment = form.save(commit=False)
            new_comment.author = request.user
            new_comment.post = post
            new_comment.parent = parent_comment
            new_comment.save()
        comments = Comment.objects.filter(comment=post).order_by('-created_on')
        context = {
            'post': post,
            'form': form,
            'comments': comments
        }
        
        return redirect('social:post-detail', context)
    
class ProfileView(View):
    def get(self, request, pk, *args, **kwargs):
        profile = UserProfile.objects.get(pk=pk)
        user = profile.user
        posts = Post.objects.filter(author=user).order_by('-created_on')
        
        followers = profile.followers.all()
        is_following = True if followers else False 
        for follower in followers:
            if follower == request.user:
                is_following = True
                break
            else:
                is_following = False
                
        number_of_followers = len(followers)
        
        context = {
            'user': user,
            'profile': profile, 
            'posts': posts,
            'is_following': is_following,
            'number_of_followers': number_of_followers,
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
        profile = self.get_object()
        return self.request.user == profile.user

class AddFollower(LoginRequiredMixin, View):
    def post(self, request, pk, *args, **kwargs):
        profile = UserProfile.objects.get(pk=pk)
        
        profile.followers.add(request.user)
        notification = Notification.objects.create(notification_type=3, form_user=request.user, to_user=profile.user)
        return redirect('social:profile', pk=pk)

class RemoveFollower(LoginRequiredMixin, View):
    def post(self,request, pk, *args, **kwargs):
        profile = UserProfile.objects.get(pk=pk)
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
        
        is_dislike = False
        for dislike in post.dislikes.all():
            if dislike == request.user:
                is_dislike = True
                break
        if is_dislike:
            post.dislikes.remove(request.user)
        is_like = False
        for like in post.likes.all():
            if like == request.user:
                is_like = True
                break
        if not is_like:
            post.likes.add(request.user)
            notification = Notification.objects.create(notification_type=1, form_user=request.user, to_user=post.author, post=post)
        if is_like:
            post.likes.remove(request.user)
            
        next = request.POST.get('next', '/social')
        return HttpResponseRedirect(next)
            
class AddDislike(LoginRequiredMixin, View):
    def post(self, request, pk, *args, **kwargs):
        post = Post.objects.get(pk=pk)
        is_like = False
        for like in post.likes.all():
            if like == request.user:
                is_like = True
                break
        if is_like:
            post.likes.remove(request.user)
        is_dislike = False
        for dislike in post.dislikes.all():
            if dislike == request.user:
                is_dislike = True
                break
            
        if not is_dislike:
            post.dislikes.add(request.user)
        if is_dislike:
            post.dislikes.remove(request.user)
        
        next = request.POST.get('next', '/social')
        return HttpResponseRedirect(next)
    
class UserSearch(View):
    def get(self,request, *args, **kwargs):
        query = self.request.GET.get('query', '')
        profile_list = UserProfile.objects.filter(
            Q(user__username__icontains=query)
        )
        
        context = {
            'profile_list': profile_list,
        }
        return render(request, 'social/search.html', context)
    
class PostNotification(View):
    def get(self, request, notification_pk, object_pk, *args, **kwargs):
        notification = Notification.objects.get(pk=notification_pk)
        post = Post.objects.get(pk=object_pk)
        
        notification.user_has_seen = True
        notification.save()
        return redirect('social:post-detail', pk=object_pk)
    
class FollowNotification(View):
    def get(self, request, notification_pk, object_pk, *args, **kwargs):
        notification = Notification.objects.get(pk=notification_pk)
        profile =UserProfile.objects.get(pk=object_pk)
        notification.user_has_seen = True
        notification.save()
        
        return redirect('social:profile', pk=object_pk)
    
class RemoveNotification(View):
    def delete(self, request, notification_pk, *args, **kwargs):
        notification = Notification.objects.get(pk=notification_pk)
        notification.user_has_seen = True
        notification.save()
        return HttpResponse('Success', content_type='text/plain')
    
class CreateThread(View):
    def get(self, request, *args, **kwargs):
        form = ThreadForm()
        context = {
            'form': form,
        }
        return render(request, 'social/create_thread.html', context)
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
        
class ListThreads(View):
    def get(self, request, *args, **kwargs):
        threads = ThreadModel.objects.filter(Q(user=request.user) | Q(receiver=request.user))
        context = {
            'threads': threads,
        }
        return render(request, 'social/inbox.html', context)
    
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
        notification = Notification.objects.create(
            notification_type=4,
            form_user=request.user,
            to_user = receiver, 
            thread=thread,
        )
        
        return redirect('social:thread', pk=pk)

class ThreadView(View):
    def get(self, request, pk, *args, **kwargs):
        form = MessageForm()
        thread =  ThreadModel.objects.get(pk=pk)
        message_list = MessageModel.objects.filter(thread__pk__contains=pk)
        
        context = {
            'thread': thread,
            'form': form,
            'message_list': message_list
        }
        return render(request, 'social/thread.html', context)