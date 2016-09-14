

class EditPostHandler(BlogHandler):
        def get(self):
            self.redirect('/blog')

        def post(self):
            if self.request.get('edit'):
                post_id = self.request.get('edit')
                post = Post.get_by_id(int(post_id), parent=blog_key())
                user_name = ""
                author = ""
                if self.user:
                    user_name = self.user.name
                    if user_name == post.author:
                        post.content = post.content.replace(
                            '<br>', '')  # remove <br>s
                        self.render('editpost.html', post=post)
                    else:
                        self.redirect('/blog')  # must be post author to edit
            elif self.request.get('delete'):
                post_id = self.request.get('delete')
                post = Post.get_by_id(int(post_id), parent=blog_key())
                post.key.delete()
                self.redirect('/blog')
            elif self.request.get('cancel'):
                post_id = self.request.get('cancel')
                self.redirect('/blog/post?post_id=' + post_id)
            elif self.request.get('update'):
                post_id = self.request.get('update')
                post = Post.get_by_id(int(post_id), parent=blog_key())
                subject = self.request.get('subject')
                content = self.request.get('content')
                content = cgi.escape(content)
                content = content.replace('\n', '<br>')
                post.subject = subject
                post.content = content
                post.put()
                self.redirect('/blog/post?post_id=' + post_id)
