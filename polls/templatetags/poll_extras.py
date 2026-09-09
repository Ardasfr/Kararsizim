from django import template

register = template.Library()

@register.filter
def has_voted(poll, request):
    """Kullanıcının ankette oy verip vermediğini denetler."""
    if not request:
        return False
    user = request.user if request.user.is_authenticated else None
    session_key = request.session.session_key
    return poll.has_user_voted(user=user, session_key=session_key)

@register.filter
def get_user_vote(poll, request):
    """Kullanıcının bu anketteki oyunu (Vote objesi) döndürür."""
    if not request:
        return None
    user = request.user if request.user.is_authenticated else None
    session_key = request.session.session_key
    return poll.user_vote(user=user, session_key=session_key)

@register.filter
def percentage(choice):
    return choice.percentage()

@register.filter
def int_percentage(choice):
    return int(round(choice.percentage()))
