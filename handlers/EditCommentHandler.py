

class EditCommentHandler(BlogHandler):
    def get(self):
        self.render('editcomment.html')
