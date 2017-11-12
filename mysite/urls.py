"""mysite URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin
from blog.views import *

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^login/$', login, name='login'),
    url(r'^logout/$', logout, name='logout'),
    url(r'^signup/$', signup, name='signup'),
    url(r'^index/$', index, name='index'),
    url(r'^dashboard/$', dashboard, name='dashboard'),
    url(r'^editprofile/$', editprofile, name='editprofile'),
    url(r'^sponsors/$', sponsors, name='sponsors'),
    url(r'^merchandise/$', merchandise, name='merchandise'),
    url(r'^addmerch/$', addmerch, name='addmerch'),
    url(r'^events/$', events, name='events'),
    url(r'^Masquerades/$', masq, name='Masquerades'),
    url(r'^WesternMusicClub/$', wmc, name='Western Music Club'),
    url(r'^QuizClub/$', quiz, name='Quiz Club'),
    url(r'^FineArtsClub/$', fac, name='Fine Arts Club'),
    url(r'^IndianMusicClub/$', imc, name='Indian Music Club'),
    url(r'^DanceFreakz/$', dfz, name='Dance Freakz'),
    url(r'^LiteraryClub/$', lit, name='Literary Club'),
    url(r'^addclubwork/$', addclubwork, name='addclubwork'),
    url(r'^members/$', members, name='members'),
    url(r'^masqmembers/$', masqmem, name='masqmem'),
    url(r'^wmcmembers/$', wmcmem, name='wmcmem'),
    url(r'^quizmembers/$', quizmem, name='quizmem'),
    url(r'^facmembers/$', facmem, name='facmem'),
    url(r'^imcmembers/$', imcmem, name='imcmem'),
    url(r'^dfzmembers/$', dfzmem, name='dfzmem'),
    url(r'^litmembers/$', litmem, name='litmem'),
    url(r'^alumini/$', alumini, name='alumini'),
    url(r'^masqalumini/$', masqalum, name='masqalum'),
    url(r'^wmcalumini/$', wmcalum, name='wmcalum'),
    url(r'^quizalumini/$', quizalum, name='quizalum'),
    url(r'^facalumini/$', facalum, name='facalum'),
    url(r'^imcalumini/$', imcalum, name='imcalum'),
    url(r'^dfzalumini/$', dfzalum, name='dfzalum'),
    url(r'^litalumini/$', litalum, name='litalum'),
    url(r'^contact/$', contact, name='contact'),
    url(r'^feedback/$', feedback, name='feedback'),
]
