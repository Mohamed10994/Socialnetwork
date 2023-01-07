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
from django.db.models import Q
from django.contrib import messages
from django.utils import timezone
from django.shortcuts import get_object_or_404

class PostListView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):

        form = PostForm()
        share_form = SharedForm()

        posts = Post.objects.get_following_posts(
            user=request.user
        )

        profile_list = UserProfile.objects.all()[:10]

        context = {
            'post_list': posts,
            'shareform': share_form,
            'form': form,
            'profile_list': profile_list

        }

        return render(request, 'social/post_list.html', context)
    
    def post(self, request, *args, **kwargs):

        posts = Post.objects.get_following_posts(
            user=request.user 
        )

        profile_list = UserProfile.objects.all()[:10]

        form = PostForm(request.POST, request.FILES)

        files = request.FILES.getlist('image')

        share_form = SharedForm()

        if form.is_valid():
            new_post = form.save(commit=False)
            new_post.assign_author(author=request.user)
            new_post.create_tags()

            for file in files:
                # img = Image(image=file)
                # img.save()
                img = Image.objects.create(
                    image=file,
                )
                new_post.image.add(img)

            # new_post.save()

        form = PostForm()

        context = {
            'post_list': posts,
            'shareform': share_form,
            'form': form,
            'profile_list': profile_list
        }
            
        return render(request, 'social/post_list.html', context)
    
class PostDetailView(LoginRequiredMixin, View):
    def get(self, request, pk, *args, **kwargs):

        post = get_object_or_404(Post, pk=pk)

        form = CommentForm()

        comments = Comment.objects.related_post(post=post)
        
        context = {
            'post': post,
            'form': form,
            'comments': comments,
        }

        return render(request, 'social/post_detail.html', context)
    
    def post(self, request, pk, *args, **kwargs):
        post = get_object_or_404(
            Post,
            pk=pk
        )
        form = CommentForm(request.POST)
        
        if form.is_valid():
            new_comment = form.save(commit=False)
            # new_comment.author = request.user
            # new_comment.post = post
            # new_comment.save()
            new_comment.save_data(
                author=request.user,
                post=post
            )
            new_comment.create_tags()
            
        comments = Comment.objects.filter(post=post)

        # notification = Notification.objects.create(notification_type=2, form_user=request.user, to_user=post.author, post=post)

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
        post = Post.objects.get(pk=post_pk)
        parent_comment = Comment.objects.get(pk=pk)
        form = CommentForm(request.POST)
        
        if form.is_valid():
            new_comment = form.save(commit=False)
            # new_comment.author = request.user
            # new_comment.post = post
            # new_comment.parent = parent_comment
            # new_comment.save()

            new_comment.save_data(
                author=request.user,
                post=post,
                parent=parent_comment
            )


        # notification = Notification.objects.create(notification_type=2, form_user=request.user, to_user=parent_comment.author, comment=new_comment)
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
        original_post = Post.objects.get(pk=pk)
        form = SharedForm(request.POST)
        
        if form.is_valid():
            # new_post = Post(
            #     shared_body = self.request.POST.get('body'),
            #     body = original_post.body,
            #     author = original_post.author,
            #     created_on = original_post.created_on,
            #     shared_user = request.user,
            #     shared_on = timezone.now(),
            # )
            # new_post.save()

            new_post = Post.objects.create(
                shared_body=self.request.POST.get('body'),
                body=original_post.body,
                author=original_post.author,
                created_on=original_post.created_on,
                shared_user=request.user,
                shared_on=timezone.now(),
            )
            
            # for img in original_post.image.all():
            #     new_post.image.add(img)
    
            new_post.image.add(*original_post.image.all())
                
            # new_post.save()
            
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
        comment = Comment.objects.get(pk=pk)

        # is_dislike = False
        
        # TODO: REMOVED - MIGHT NEED TO BE BACK.
        # for dislike in comment.dislikes.all():
        #     if dislike == request.user:
        #         is_dislike = True
        #         break
        # if is_dislike:
        #     comment.dislikes.remove(request.user)
        
        # NOTE: Replaced with below.
        # is_like = False
        # for like in comment.likes.all():
        #     if like == request.user:
        #         is_like = True
        #         break
        # if not is_like:
        #     comment.likes.add(request.user)
        #     notification = Notification.objects.create(notification_type=1, form_user=request.user, to_user=comment.author, comment=comment)
        # if is_like:
        #     comment.likes.remove(request.user)

        if comment.likes.filter(pk=request.user.pk).exists():
            comment.likes.remove(request.user)
        else:
            # Notification.objects.create(notification_type='LIKE', form_user=request.user, to_user=comment.author, comment=comment)
            Notification.objects.add_like(
                form_user=request.user,
                to_user=comment.author,
                comment=comment
            )
            comment.likes.add(request.user)

        next = request.POST.get('next', '/  ')
        return HttpResponseRedirect(next)

class AddCommentDislike(LoginRequiredMixin, View):
    def post(self, request, pk, *args, **kwargs):
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
        next = request.POST.get('next', '/')
        return HttpResponseRedirect(next)
            

    
class ProfileView(View):
    def get(self, request, pk, *args, **kwargs):
        profile = UserProfile.objects.get(pk=pk)
        # user = profile.user

        posts = Post.objects.filter(
            author=profile.user
        ).order_by(
            '-created_on'
        )
        
        # followers = profile.followers.all()
        # is_following = True if followers else False 
        # for follower in followers:
        #     if follower == request.user:
        #         is_following = True
        #         break
        #     else:
        #         is_following = False

        # number_of_followers = len(followers)


        followers = profile.followers.values(
            'profile__pk',
            'username',
            'profile__picture'
        )

        context = {
            # 'user': user,
            'profile': profile, 
            'posts': posts,
            'is_following': profile.followers.filter(pk=request.user.pk).exists(),
            'number_of_followers': followers.count(),
            'followers': followers
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
        profile = UserProfile.objects.get(pk=pk)
        
        profile.followers.add(request.user)
        # Notification.objects.create(notification_type=3, form_user=request.user, to_user=profile.user)
        Notification.objects.add_follower(
            form_user=request.user,
            to_user=profile.user
        )

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
            # notification = Notification.objects.create(notification_type=1, form_user=request.user, to_user=post.author, post=post)
            Notification.objects.add_like(
                form_user=request.user,
                to_user=post.author,
                post=post
            )

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
        qs = UserProfile.objects.search(query=query)
    
        context = {
            'object_list': qs,
        }
        return render(request, 'social/search.html', context)
    
class PostNotification(View):
    def get(self, request, notification_pk, post_pk, *args, **kwargs):
        # post = Post.objects.get(pk=post_pk)

        # notification = Notification.objects.get(pk=notification_pk)
        # notification.user_has_seen = True
        # notification.save()

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
        except User.DoesNotExist:
            messages.error(request, 'User not found.')
            return redirect('social:create-thread')

        thread_pk = ThreadModel.objects.filter(user=request.user, receiver=receiver).values_list('pk', flat=True).first()

        if thread_pk:
            return redirect('social:thread', pk=thread_pk)

        if form.is_valid():
            # sender_thread = ThreadModel(
            #     user=request.user,
            #     receiver=receiver,
            # )
            # sender_thread.save()
            sender_thread = ThreadModel.objects.create(
                user=request.user,
                receiver=receiver,
            )

            thread_pk = sender_thread.pk
            return redirect('social:thread', pk=thread_pk)


class ListThreads(View):
    def get(self, request, *args, **kwargs):
        form = ThreadForm()
        threads = ThreadModel.objects.filter(Q(user=request.user) | Q(receiver=request.user))
        context = {
            'threads': threads,
            'form': form,
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
        # notification = Notification.objects.create(
        #     notification_type=4,
        #     form_user=request.user,
        #     to_user = receiver, 
        #     thread=thread,
        # )
        
        Notification.objects.add_dm(
            form_user=request.user,
            to_user = receiver, 
            thread=thread
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
        