def context(request):
    data = dict()
    
    user_agent = request.META.get('HTTP_USER_AGENT', '')
    
    data['iphone_version'] = False
    if user_agent.count('iPhone') and user_agent.count('AppleWebKit'):
        data['iphone_version'] = True
        
    
    return data