"""
ASGI config for IKA_NET_HMS project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.1/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "IKA_NET_HMS.settings")

application = get_asgi_application()

# import os
# from django.core.asgi import get_asgi_application

# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'IKA_NET_HMS.settings')

# from channels.auth import AuthMiddlewareStack
# from channels.routing import ProtocolTypeRouter , URLRouter
# from I_CARE import routing

# application = ProtocolTypeRouter(
# 	{
# 		"http" : get_asgi_application() ,
# 		"websocket" : AuthMiddlewareStack(
# 			URLRouter(
# 				routing.websocket_urlpatterns
# 			)
# 		)
# 	}
# )

