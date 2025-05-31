#!/home/stepsizestrategies/.local/bin/python3



from django.conf.urls import url,include


import strategies.views



# Uncomment the next lines to enable the admin:
# from django.conf.urls import include
from django.contrib import admin
admin.autodiscover()

urlpatterns = [
    # Examples:

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
     url(r'^admin/', include(admin.site.urls)),

       url(r'^hatanalizi/$', strategies.views.hatanalizi, name='hatanalizi'),

         url(r'^hatanalizicl/$', strategies.views.hatanalizicl, name='hatanalizicl'),

        url(r'^hatanaliziclf/$', strategies.views.hatanaliziclf, name='hatanaliziclf'),

          url(r'^picard/$', strategies.views.picard, name='picard'),

         url(r'^strategiess/$', strategies.views.strategiess, name='strategiess'),

         url(r'^picardcl/$', strategies.views.picardcl, name='picardcl'),

         url(r'^picardclf/$', strategies.views.picardclf, name='picardclf'),

         url(r'^pihata/$', strategies.views.pihata, name='pihata'),

         url(r'^pihatacl/$', strategies.views.pihatacl, name='pihatacl'),
          url(r'^pihataclf/$', strategies.views.pihataclf, name='pihataclf'),


       url(r'^$', strategies.views.index, name='index'),


url(r'^sisalgo1/$', strategies.views.sisalgo1, name='sisalgo1'),

url(r'^sisalgocl1/$', strategies.views.sisalgocl1, name='sisalgocl1'),
url(r'^sisalgocl2/$', strategies.views.sisalgocl2, name='sisalgocl2'),
url(r'^sisalgocl3/$', strategies.views.sisalgocl3, name='sisalgocl3'),


url(r'^sisalgoclf1/$', strategies.views.sisalgoclf1, name='sisalgoclf1'),
url(r'^sisalgoclf2/$', strategies.views.sisalgoclf2, name='sisalgoclf2'),
url(r'^sisalgoclf3/$', strategies.views.sisalgoclf3, name='sisalgoclf3'),


url(r'^nonsisalgo1/$', strategies.views.nonsisalgo1, name='nonsisalgo1'),

url(r'^nonsisalgocl1/$', strategies.views.nonsisalgocl1, name='nonsisalgocl1'),
url(r'^nonsisalgocl2/$', strategies.views.nonsisalgocl2, name='nonsisalgocl2'),
url(r'^nonsisalgocl3/$', strategies.views.nonsisalgocl3, name='nonsisalgocl3'),

url(r'^nonsisalgoclf1/$', strategies.views.nonsisalgoclf1, name='nonsisalgoclf1'),
url(r'^nonsisalgoclf2/$', strategies.views.nonsisalgoclf2, name='nonsisalgoclf2'),
url(r'^nonsisalgoclf3/$', strategies.views.nonsisalgoclf3, name='nonsisalgoclf3'),






       url(r'^login/$', strategies.views.login_view, name="login"),

    url(r'^register/$', strategies.views.register_view, name="register_view"),

    url(r'^logout/$', strategies.views.logout_view, name="logout"),

     url(r'^about/$', strategies.views.about, name="about"),





]