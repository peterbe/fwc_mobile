from django.utils.html import strip_spaces_between_tags as short


## http://www.davidcramer.net/code/369/spaceless-html-in-django.html
class SpacelessMiddleware(object):
    def process_response(self, request, response):
        if 'text/html' in response['Content-Type']:
            response.content = short(response.content)
        return response