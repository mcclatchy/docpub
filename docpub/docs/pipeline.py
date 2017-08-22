# extending python-social-auth pipeline options
from django.contrib.auth.models import Group #, User
# from django.core.mail import send_mail
from docpub.settings import APP_DOMAIN, EMAIL_RECIPIENT, EMAIL_SENDER, SLACK_USER
from docs.slackbot import slackbot


def apply_permissions(backend, user, response, *args, **kwargs):
    ## if the user hasn't logged in before
    if not user.last_login:
        ## get the add/edit/delete group
        group = Group.objects.get(name__contains='add/edit/delete documents')
        ## add the user to that group
        group.user_set.add(user)
        ## get the edit user group
        group = Group.objects.get(name__contains='edit user')
        ## add the user to that group
        group.user_set.add(user)
        ## set the user as staff
        user.is_staff = True
        user.save()

# def email_admins(backend, user, response, *args, **kwargs):
#     if not user.last_login:
#         recipients = [EMAIL_RECIPIENT]
#         subject = 'New user registered: {user}'.format(user=user)
#         message = None
#         html_message = 'Edit user profile:<br> {domain}/admin/auth/user/{id}/change/'.format(domain=APP_DOMAIN, id=user.id)
#         send_mail(
#             subject, ## subject (string)
#             message, ## message (string)
#             EMAIL_SENDER, ## sender (string)
#             recipients, ## recipients (list)
#             fail_silently=False,
#             html_message=html_message,
#     )

def slack_notify(backend, user, response, *args, **kwargs):
    if not user.last_login:
        message = '{notify} New user registered: {user}\n\n Edit user profile:\n http://{domain}/admin/auth/user/{id}/change/'.format(notify=SLACK_USER, user=user, domain=APP_DOMAIN, id=user.id)
        slackbot(message)

