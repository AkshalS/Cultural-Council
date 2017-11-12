from django.shortcuts import render, render_to_response, get_object_or_404, redirect
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib import messages
from django.contrib import auth
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from django.views.decorators.csrf import csrf_protect
from django.core.urlresolvers import reverse
from django.db import connection, IntegrityError, transaction
from datetime import datetime, date
import re



def index(request):
	userid=request.user.username
	cursor=connection.cursor()
	cursor.execute('SELECT poster, ideve from events')
	results=cursor.fetchall()
	for i in range(0, len(results)):
		try:
			write_file(results[i][0], './static/temp/img'+str(results[i][1])+'.jpg')
		except:
			pass
	cursor.execute('SELECT ideve, name, cont, dated, timed from events order by dated desc, timed desc limit 6')
	results=cursor.fetchall()
	dat=[]
	i=0
	for j in range(0, len(results)):
		dat.append(results[j] + ("./temp/img" + str(results[j][0]) + ".jpg" , ))
	data=tuple(dat)
	return render(request, 'index.html', {'uid':userid, 'data':data})

def write_file(data, filename):
	with open(filename, 'wb') as f:
		f.write(data)

@csrf_protect
def login(request):
	if request.user.is_authenticated():	
		return HttpResponseRedirect(reverse('index'))
	if request.POST:
		username = request.POST['uname']
		password = request.POST['psw']
		if username == '':
			return render(request, 'login.html')

		cursor = connection.cursor()
		cursor.execute("SELECT * from auth_user where username='"+username+"';")
		data = cursor.fetchone()
		connection.close()

		if data is not None:
			username = data[4]
			print username, password
			user = auth.authenticate(username=username, password=password)
			if user is not None:
				auth.login(request, user)											
				return HttpResponseRedirect(reverse('index'))
			else:																	
				messages.error(request, 'The username and password combination is incorrect.')
		else:
			messages.error(request, 'This ID is not registered.')						
	return render(request, 'login.html')


def signup(request):
	if request.method=="POST":
		name=request.POST.get("name")
		email=request.POST.get("email")
		uname=request.POST.get("uname")
		psw1=request.POST.get("psw1")
		psw2=request.POST.get("psw2")
		mob=request.POST.get("mob")
		branch=request.POST.get("branch")
		batch=request.POST.get("batch")
		if int(batch)<=int(datetime.now().year):
			post="Alumini"
		else:
			post="Participant"
		alph="abcdefghijklmnopqrstuvwxyz ABCDEFGHIJKLMNOPQRSTUVWXYZ"
		digit="0123456789_"
		data=[]
		cursor = connection.cursor()
		cursor.execute("SELECT username from auth_user")
		data = cursor.fetchall()
		flag=False
		for i in data:
			if i[0]==uname:
				flag=True
		if flag==True:
			messages.error(request, 'The username already exists.')
			return HttpResponseRedirect(reverse('signup'))
		data2=[]
		cursor.execute("SELECT email from auth_user")
		data2 = cursor.fetchall()
		flag=False
		for i in data2:
			if i[0]==email:
				flag=True
		if flag==True:
			messages.error(request, 'The emailid already registered.')
			return HttpResponseRedirect(reverse('signup'))
		if len(psw1)<8:
			messages.error(request, 'The password should have atleast 8 characters.')
			return HttpResponseRedirect(reverse('signup'))
		if psw1!=psw2:
			messages.error(request, 'The password is not same in both fields.')
			return HttpResponseRedirect(reverse('signup'))
		passwrd=make_password(psw1)
		flag=True
		for i in name:
			if i not in alph:
				flag=False
		if flag==False:
			messages.error(request, 'Name should contain only letters')
			return HttpResponseRedirect(reverse('signup'))
		flag=True
		for i in uname:
			if i not in alph and i not in digit:
				flag=False
		if flag==False:
			messages.error(request, 'Username should contain only letters, numbers and _ ')
			return HttpResponseRedirect(reverse('signup'))
		flag=True
		if '@' not in email:
			flag=False
		if '.' not in email:
			flag=False
		if flag==False:
			messages.error(request, 'Enter proper email address')
			return HttpResponseRedirect(reverse('signup'))
		flag=True
		for i in mob:
			if i>'9' or i<'0':
				flag=False
			if i not in digit:
				flag=False
		if len(mob)!=10 or flag==False:
			messages.error(request, 'Enter correct mob no.')
			return HttpResponseRedirect(reverse('signup'))
		flag=True
		for i in batch:
			if i not in digit:
				flag=False
		if len(batch)!=4 or flag==False:
			messages.error(request, 'Enter correct batch')
			return HttpResponseRedirect(reverse('signup'))
		cursor.execute('INSERT into auth_user (password, last_login, is_superuser, username, first_name, last_name, email ,is_staff, is_active, date_joined, branch, club, mob, batch, post) values ("%s", NULL, 0, "%s", "%s", NULL, "%s", 0, 1, "%s", "%s", NULL, "%s", %d, "%s");'%(str(passwrd), str(uname), str(name), str(email), str(datetime.now()), str(branch), str(mob), int(batch), str(post) ))
		messages.error(request, 'Signed Up Successfully')
		return HttpResponseRedirect(reverse('login'))
	return render(request, 'signup.html', {})

def contact(request):
	date=datetime.now()
	userid1=request.user.username
	alph="abcdefghijklmnopqrstuvwxyz ABCDEFGHIJKLMNOPQRSTUVWXYZ"
	digit="0123456789_"
	if request.user.is_authenticated():
		mailid1=request.user.email
	else:
		mailid1=""
	if request.method=="POST":
		if request.user.is_authenticated():
			userid=request.user.username
			mailid=request.user.email
		else:
			userid=request.POST.get("name")
			mailid=request.POST.get("mailid")
		sub=request.POST.get("subject")
		cont=request.POST.get("content")
		flag=True
		for i in userid:
			if i not in alph:
				flag=False
		if flag==False:
			messages.error(request, 'Name should contain only letters, numbers and _ ')
			return HttpResponseRedirect(reverse('contact'))
		flag=True
		if '@' not in mailid:
			flag=False
		if '.' not in mailid:
			flag=False
		if flag==False:
			messages.error(request, 'Enter proper email address')
			return HttpResponseRedirect(reverse('contact'))
		if not request.user.is_authenticated():
			data=[]
			cursor = connection.cursor()
			cursor.execute("SELECT username from auth_user")
			data = cursor.fetchall()
			flag=False
			for i in data:
				if i[0]==userid:
					flag=True
			if flag==True:
				messages.error(request, 'The username already registered. Login to give feedback')
				return HttpResponseRedirect(reverse('contact'))
			data2=[]
			cursor.execute("SELECT email from auth_user")
			data2 = cursor.fetchall()
			flag=False
			for i in data2:
				if i[0]==mailid:
					flag=True
			if flag==True:
				messages.error(request, 'The emailid already registered.Login to give feedback')
				return HttpResponseRedirect(reverse('contact'))
		cursor = connection.cursor()
		cursor.execute('INSERT into feedback (username, mailid, date_time, subject, content) values ("%s", "%s", "%s", "%s", "%s");'%(str(userid), str(mailid), str(datetime.now()), str(sub), str(cont) ))
		messages.error(request, 'Feedback Recorded')
		return HttpResponseRedirect(reverse('contact'))
	return render(request, 'contact.html', {'uid':userid1, 'mid':mailid1})

def feedback(request):
	userid=request.user.username
	data=[]
	cursor = connection.cursor()
	cursor.execute("SELECT * from feedback")
	data = cursor.fetchall()
	return render(request, 'feedback.html', {'uid':userid , 'fbdata':data})

def members(request):
	userid=request.user.username
	data=[]
	this_year = datetime.now().year
	club = "Cultural Council"
	cursor = connection.cursor()
	cursor.execute('SELECT * from auth_user where batch>"%s" order by first_name; '%str(this_year))
	data = cursor.fetchall()
	if request.method=="POST":
		uname=request.POST.get("uname")
		clubname=request.POST.get("clubname")
		postname=request.POST.get("postname")
		isu=0
		istf=0
		if postname=="General Secretary" or postname=="Joint General Secretary":
			isu=1
		else:
			isu=0
		if postname=="Club Secretary" or postname=="Joint Secretary":
			istf=1
		else:
			istf=0
		cursor = connection.cursor()
		cursor.execute('Update auth_user set club="%s", post="%s", is_superuser="%d", is_staff="%d" where username="%s";'%(str(clubname), str(postname), int(isu), int(istf), str(uname) ))
		messages.error(request, 'Profile Updated Successfully')
		if postname=="Alumini":
			return HttpResponseRedirect(reverse('alumini'))
		else:
			return HttpResponseRedirect(reverse('members'))
	return render(request, 'members.html', {'uid':userid, 'fbdata':data, 'clubname':club, 'alum':1, 'mem':1})

def masqmem(request):
	userid=request.user.username
	data=[]
	this_year = datetime.now().year
	club = "Masquerades"
	cursor = connection.cursor()
	cursor.execute('SELECT * from auth_user where batch>"%s" and club="%s" order by post; '%(str(this_year), str(club) ))
	data = cursor.fetchall()
	return render(request, 'members.html', {'uid':userid, 'fbdata':data, 'clubname':club, 'alum':1, 'mem':0})

def wmcmem(request):
	userid=request.user.username
	data=[]
	this_year = datetime.now().year
	club = "Western Music Club"
	cursor = connection.cursor()
	cursor.execute('SELECT * from auth_user where batch>"%s" and club="%s" order by post; '%(str(this_year), str(club) ))
	data = cursor.fetchall()
	return render(request, 'members.html', {'uid':userid, 'fbdata':data, 'clubname':club, 'alum':1, 'mem':0})

def quizmem(request):
	userid=request.user.username
	data=[]
	this_year = datetime.now().year
	club = "Quiz Club"
	cursor = connection.cursor()
	cursor.execute('SELECT * from auth_user where batch>"%s" and club="%s" order by post; '%(str(this_year), str(club) ))
	data = cursor.fetchall()
	return render(request, 'members.html', {'uid':userid, 'fbdata':data, 'clubname':club, 'alum':1, 'mem':0})

def facmem(request):
	userid=request.user.username
	data=[]
	this_year = datetime.now().year
	club = "Fine Arts Club"
	cursor = connection.cursor()
	cursor.execute('SELECT * from auth_user where batch>"%s" and club="%s" order by post; '%(str(this_year), str(club) ))
	data = cursor.fetchall()
	return render(request, 'members.html', {'uid':userid, 'fbdata':data, 'clubname':club, 'alum':1, 'mem':0})

def imcmem(request):
	userid=request.user.username
	data=[]
	this_year = datetime.now().year
	club = "Indian Music CLub"
	cursor = connection.cursor()
	cursor.execute('SELECT * from auth_user where batch>"%s" and club="%s" order by post; '%(str(this_year), str(club) ))
	data = cursor.fetchall()
	return render(request, 'members.html', {'uid':userid, 'fbdata':data, 'clubname':club, 'alum':1, 'mem':0})

def dfzmem(request):
	userid=request.user.username
	data=[]
	this_year = datetime.now().year
	club = "Dance Freakz"
	cursor = connection.cursor()
	cursor.execute('SELECT * from auth_user where batch>"%s" and club="%s" order by post; '%(str(this_year), str(club) ))
	data = cursor.fetchall()
	return render(request, 'members.html', {'uid':userid, 'fbdata':data, 'clubname':club, 'alum':1, 'mem':0})

def litmem(request):
	userid=request.user.username
	data=[]
	this_year = datetime.now().year
	club = "Literary Club"
	cursor = connection.cursor()
	cursor.execute('SELECT * from auth_user where batch>"%s" and club="%s" order by post; '%(str(this_year), str(club) ))
	data = cursor.fetchall()
	return render(request, 'members.html', {'uid':userid, 'fbdata':data, 'clubname':club, 'alum':1, 'mem':0})

def alumini(request):
	userid=request.user.username
	data=[]
	this_year = datetime.now().year
	club = "Cultural Council"
	cursor = connection.cursor()
	cursor.execute('SELECT * from auth_user where batch<="%s" order by first_name; '%str(this_year))
	data = cursor.fetchall()
	return render(request, 'members.html', {'uid':userid, 'fbdata':data, 'clubname':club, 'alum':0, 'mem':1})

def masqalum(request):
	userid=request.user.username
	data=[]
	this_year = datetime.now().year
	club = "Masquerades"
	cursor = connection.cursor()
	cursor.execute('SELECT * from auth_user where batch<="%s" and club="%s" order by first_name; '%(str(this_year), str(club) ))
	data = cursor.fetchall()
	return render(request, 'members.html', {'uid':userid, 'fbdata':data, 'clubname':club, 'alum':0, 'mem':0})

def wmcalum(request):
	userid=request.user.username
	data=[]
	this_year = datetime.now().year
	club = "Western Music Club"
	cursor = connection.cursor()
	cursor.execute('SELECT * from auth_user where batch<="%s" and club="%s" order by first_name; '%(str(this_year), str(club) ))
	data = cursor.fetchall()
	return render(request, 'members.html', {'uid':userid, 'fbdata':data, 'clubname':club, 'alum':0, 'mem':0})

def quizalum(request):
	userid=request.user.username
	data=[]
	this_year = datetime.now().year
	club = "Quiz Club"
	cursor = connection.cursor()
	cursor.execute('SELECT * from auth_user where batch<="%s" and club="%s" order by first_name; '%(str(this_year), str(club) ))
	data = cursor.fetchall()
	return render(request, 'members.html', {'uid':userid, 'fbdata':data, 'clubname':club, 'alum':0, 'mem':0})

def facalum(request):
	userid=request.user.username
	data=[]
	this_year = datetime.now().year
	club = "Fine Arts Club"
	cursor = connection.cursor()
	cursor.execute('SELECT * from auth_user where batch<="%s" and club="%s" order by first_name; '%(str(this_year), str(club) ))
	data = cursor.fetchall()
	return render(request, 'members.html', {'uid':userid, 'fbdata':data, 'clubname':club, 'alum':0, 'mem':0})

def imcalum(request):
	userid=request.user.username
	data=[]
	this_year = datetime.now().year
	club = "Indian Music Club"
	cursor = connection.cursor()
	cursor.execute('SELECT * from auth_user where batch<="%s" and club="%s" order by first_name; '%(str(this_year), str(club) ))
	data = cursor.fetchall()
	return render(request, 'members.html', {'uid':userid, 'fbdata':data, 'clubname':club, 'alum':0, 'mem':0})

def dfzalum(request):
	userid=request.user.username
	data=[]
	this_year = datetime.now().year
	club = "Dance Freakz"
	cursor = connection.cursor()
	cursor.execute('SELECT * from auth_user where batch<="%s" and club="%s" order by first_name; '%(str(this_year), str(club) ))
	data = cursor.fetchall()
	return render(request, 'members.html', {'uid':userid, 'fbdata':data, 'clubname':club, 'alum':0, 'mem':0})

def litalum(request):
	userid=request.user.username
	data=[]
	this_year = datetime.now().year
	club = "Literary Club"
	cursor = connection.cursor()
	cursor.execute('SELECT * from auth_user where batch<="%s" and club="%s" order by first_name; '%(str(this_year), str(club) ))
	data = cursor.fetchall()
	return render(request, 'members.html', {'uid':userid, 'fbdata':data, 'clubname':club, 'alum':0, 'mem':0})

def events(request):
	userid=request.user.username
	cursor=connection.cursor()
	cursor.execute('SELECT poster, ideve from events')
	results=cursor.fetchall()
	for i in range(0, len(results)):
		try:
			write_file(results[i][0], './static/temp/img'+str(results[i][1])+'.jpg')
		except:
			pass
	cursor.execute('SELECT ideve, name, cont, dated, timed from events order by dated desc, timed desc')
	results=cursor.fetchall()
	dat=[]
	i=0
	for j in range(0, len(results)):
		dat.append(results[j] + ("./temp/img" + str(results[j][0]) + ".jpg" , ))
	data=tuple(dat)
	if request.method=="POST":
		name=request.POST.get("name")
		dated=request.POST.get("dated")
		timed=request.POST.get("timed")
		venue=request.POST.get("venue")
		club=request.POST.get("club")
		cont=request.POST.get("cont")
		poster=request.FILES['poster'].read()
		alph="abcdefghijklmnopqrstuvwxyz ABCDEFGHIJKLMNOPQRSTUVWXYZ"
		digit="0123456789_"
		flag=True
		for i in name:
			if i not in alph:
				flag=False
		if flag==False:
			messages.error(request, 'Name should contain only letters')
			return HttpResponseRedirect(reverse('events'))
		flag=True
		cursor = connection.cursor()
		cursor.execute('INSERT into events (name, poster, dated, timed, venue, club, cont) values (%s, %s, %s, %s, %s, %s, %s);',(str(name), str(poster), str(dated), str(timed), str(venue), str(club), str(cont) ))
		messages.error(request, 'Uploaded Successfully')
		return HttpResponseRedirect(reverse('events'))
	return render(request, 'events.html', {'uid':userid, 'data':data, 'i':0})

def masq(request):
	userid=request.user.username
	club="Masquerades"
	color="rgb(139, 131, 190)"
	cursor=connection.cursor()
	cursor.execute('SELECT logo, name from club where name=%s;',[ str(club) ])
	results=cursor.fetchall()
	for i in range(0, len(results)):
		try:
			write_file(results[i][0], './static/temp/img'+str(results[i][1])+'.jpg')
		except:
			pass
	cursor.execute('SELECT name, room, floor, hostel, fb, det from club where name=%s;',[ str(club) ])
	results=cursor.fetchall()
	dat=[]
	i=0
	for j in range(0, len(results)):
		dat.append(results[j] + ("./temp/img" + str(results[j][0]) + ".jpg" , ))
	data=tuple(dat)
	cursor.execute('SELECT first_name, username from auth_user where club=%s and post=%s;',[str(club),"Club Secretary"])
	secy=cursor.fetchall()
	cursor.execute('SELECT first_name, username from auth_user where club=%s and post=%s;',[str(club),"Joint Secretary"])
	jsecy=cursor.fetchall()
	allow=0
	if request.user.is_staff:
		for i in secy:
			if userid==i[1]:
				allow=1
		for i in jsecy:
			if userid==i[1]:
				allow=1
	cursor.execute('SELECT image, idcw from clubworks where club=%s;',[ str(club) ])
	res=cursor.fetchall()
	for i in range(0, len(res)):
		try:
			write_file(res[i][0], './static/temp/img'+str(res[i][1])+'.jpg')
		except:
			pass
	cursor.execute('SELECT idcw, name, club, date_time from clubworks where club=%s order by date_time DESC;',[ str(club) ])
	res=cursor.fetchall()
	rcw=[]
	i=0
	for j in range(0, len(res)):
		rcw.append(res[j] + ("./temp/img" + str(res[j][0]) + ".jpg" , ))
	cw=tuple(rcw)
	if request.method=="POST":
		room=request.POST.get("room")
		floor=request.POST.get("floor")
		hostel=request.POST.get("hostel")
		fb=request.POST.get("fb")
		det=request.POST.get("det")
		logo=request.FILES['logo'].read()
		cursor = connection.cursor()
		cursor.execute('UPDATE club set logo=%s, room=%s, floor=%s, hostel=%s, fb=%s, det=%s where name=%s;',[str(logo), str(room), str(floor), str(hostel), str(fb), str(det), (str(club))] )
		messages.error(request, 'Updated Successfully')
		return HttpResponseRedirect(reverse('Masquerades'))
	return render(request, 'club.html', {'uid':userid, 'frm':"/Masquerades/", 'data':data, 'color':color, 'secy':secy, 'jsecy':jsecy, 'allow':allow, 'cw':cw})

def wmc(request):
	userid=request.user.username
	club="Western Music Club"
	color="rgb(107, 162, 184)"
	cursor=connection.cursor()
	cursor.execute('SELECT logo, name from club where name=%s;',[ str(club) ])
	results=cursor.fetchall()
	for i in range(0, len(results)):
		try:
			write_file(results[i][0], './static/temp/img'+str(results[i][1])+'.jpg')
		except:
			pass
	cursor.execute('SELECT name, room, floor, hostel, fb, det from club where name=%s;',[ str(club) ])
	results=cursor.fetchall()
	dat=[]
	i=0
	for j in range(0, len(results)):
		dat.append(results[j] + ("./temp/img" + str(results[j][0]) + ".jpg" , ))
	data=tuple(dat)
	cursor.execute('SELECT first_name, username from auth_user where club=%s and post=%s;',[str(club),"Club Secretary"])
	secy=cursor.fetchall()
	cursor.execute('SELECT first_name, username from auth_user where club=%s and post=%s;',[str(club),"Joint Secretary"])
	jsecy=cursor.fetchall()
	allow=0
	if request.user.is_staff:
		for i in secy:
			if userid==i[1]:
				allow=1
		for i in jsecy:
			if userid==i[1]:
				allow=1
	cursor.execute('SELECT image, idcw from clubworks where club=%s;',[ str(club) ])
	res=cursor.fetchall()
	for i in range(0, len(res)):
		try:
			write_file(res[i][0], './static/temp/img'+str(res[i][1])+'.jpg')
		except:
			pass
	cursor.execute('SELECT idcw, name, club, date_time from clubworks where club=%s order by date_time DESC;',[ str(club) ])
	res=cursor.fetchall()
	rcw=[]
	i=0
	for j in range(0, len(res)):
		rcw.append(res[j] + ("./temp/img" + str(res[j][0]) + ".jpg" , ))
	cw=tuple(rcw)
	if request.method=="POST":
		room=request.POST.get("room")
		floor=request.POST.get("floor")
		hostel=request.POST.get("hostel")
		fb=request.POST.get("fb")
		det=request.POST.get("det")
		logo=request.FILES['logo'].read()
		cursor = connection.cursor()
		cursor.execute('UPDATE club set logo=%s, room=%s, floor=%s, hostel=%s, fb=%s, det=%s where name=%s;',[str(logo), str(room), str(floor), str(hostel), str(fb), str(det), (str(club))] )
		messages.error(request, 'Updated Successfully')
		return HttpResponseRedirect(reverse('Western Music Club'))
	return render(request, 'club.html', {'uid':userid, 'frm':"/WesternMusicClub/", 'data':data, 'color':color, 'secy':secy, 'jsecy':jsecy, 'allow':allow, 'cw':cw})

def quiz(request):
	userid=request.user.username
	club="Quiz Club"
	color="rgb(110, 202, 222)"
	cursor=connection.cursor()
	cursor.execute('SELECT logo, name from club where name=%s;',[ str(club) ])
	results=cursor.fetchall()
	for i in range(0, len(results)):
		try:
			write_file(results[i][0], './static/temp/img'+str(results[i][1])+'.jpg')
		except:
			pass
	cursor.execute('SELECT name, room, floor, hostel, fb, det from club where name=%s;',[ str(club) ])
	results=cursor.fetchall()
	dat=[]
	i=0
	for j in range(0, len(results)):
		dat.append(results[j] + ("./temp/img" + str(results[j][0]) + ".jpg" , ))
	data=tuple(dat)
	cursor.execute('SELECT first_name, username from auth_user where club=%s and post=%s;',[str(club),"Club Secretary"])
	secy=cursor.fetchall()
	cursor.execute('SELECT first_name, username from auth_user where club=%s and post=%s;',[str(club),"Joint Secretary"])
	jsecy=cursor.fetchall()
	allow=0
	if request.user.is_staff:
		for i in secy:
			if userid==i[1]:
				allow=1
		for i in jsecy:
			if userid==i[1]:
				allow=1
	cursor.execute('SELECT image, idcw from clubworks where club=%s;',[ str(club) ])
	res=cursor.fetchall()
	for i in range(0, len(res)):
		try:
			write_file(res[i][0], './static/temp/img'+str(res[i][1])+'.jpg')
		except:
			pass
	cursor.execute('SELECT idcw, name, club, date_time from clubworks where club=%s order by date_time DESC;',[ str(club) ])
	res=cursor.fetchall()
	rcw=[]
	i=0
	for j in range(0, len(res)):
		rcw.append(res[j] + ("./temp/img" + str(res[j][0]) + ".jpg" , ))
	cw=tuple(rcw)
	if request.method=="POST":
		room=request.POST.get("room")
		floor=request.POST.get("floor")
		hostel=request.POST.get("hostel")
		fb=request.POST.get("fb")
		det=request.POST.get("det")
		logo=request.FILES['logo'].read()
		cursor = connection.cursor()
		cursor.execute('UPDATE club set logo=%s, room=%s, floor=%s, hostel=%s, fb=%s, det=%s where name=%s;',[str(logo), str(room), str(floor), str(hostel), str(fb), str(det), (str(club))] )
		messages.error(request, 'Updated Successfully')
		return HttpResponseRedirect(reverse('Quiz Club'))
	return render(request, 'club.html', {'uid':userid, 'frm':"/QuizClub/", 'data':data, 'color':color, 'secy':secy, 'jsecy':jsecy, 'allow':allow, 'cw':cw})

def fac(request):
	userid=request.user.username
	club="Fine Arts Club"
	color="rgb(49, 177, 81)"
	cursor=connection.cursor()
	cursor.execute('SELECT logo, name from club where name=%s;',[ str(club) ])
	results=cursor.fetchall()
	for i in range(0, len(results)):
		try:
			write_file(results[i][0], './static/temp/img'+str(results[i][1])+'.jpg')
		except:
			pass
	cursor.execute('SELECT name, room, floor, hostel, fb, det from club where name=%s;',[ str(club) ])
	results=cursor.fetchall()
	dat=[]
	i=0
	for j in range(0, len(results)):
		dat.append(results[j] + ("./temp/img" + str(results[j][0]) + ".jpg" , ))
	data=tuple(dat)
	cursor.execute('SELECT first_name, username from auth_user where club=%s and post=%s;',[str(club),"Club Secretary"])
	secy=cursor.fetchall()
	cursor.execute('SELECT first_name, username from auth_user where club=%s and post=%s;',[str(club),"Joint Secretary"])
	jsecy=cursor.fetchall()
	allow=0
	if request.user.is_staff:
		for i in secy:
			if userid==i[1]:
				allow=1
		for i in jsecy:
			if userid==i[1]:
				allow=1
	cursor.execute('SELECT image, idcw from clubworks where club=%s;',[ str(club) ])
	res=cursor.fetchall()
	for i in range(0, len(res)):
		try:
			write_file(res[i][0], './static/temp/img'+str(res[i][1])+'.jpg')
		except:
			pass
	cursor.execute('SELECT idcw, name, club, date_time from clubworks where club=%s order by date_time DESC;',[ str(club) ])
	res=cursor.fetchall()
	rcw=[]
	i=0
	for j in range(0, len(res)):
		rcw.append(res[j] + ("./temp/img" + str(res[j][0]) + ".jpg" , ))
	cw=tuple(rcw)
	if request.method=="POST":
		room=request.POST.get("room")
		floor=request.POST.get("floor")
		hostel=request.POST.get("hostel")
		fb=request.POST.get("fb")
		det=request.POST.get("det")
		logo=request.FILES['logo'].read()
		cursor = connection.cursor()
		cursor.execute('UPDATE club set logo=%s, room=%s, floor=%s, hostel=%s, fb=%s, det=%s where name=%s;',[str(logo), str(room), str(floor), str(hostel), str(fb), str(det), (str(club))] )
		messages.error(request, 'Updated Successfully')
		return HttpResponseRedirect(reverse('Fine Arts Club'))
	return render(request, 'club.html', {'uid':userid, 'frm':"/FineArtsClub/", 'data':data, 'color':color, 'secy':secy, 'jsecy':jsecy, 'allow':allow, 'cw':cw})

def imc(request):
	userid=request.user.username
	club="Indian Music Club"
	color="rgb(233, 185, 56)"
	cursor=connection.cursor()
	cursor.execute('SELECT logo, name from club where name=%s;',[ str(club) ])
	results=cursor.fetchall()
	for i in range(0, len(results)):
		try:
			write_file(results[i][0], './static/temp/img'+str(results[i][1])+'.jpg')
		except:
			pass
	cursor.execute('SELECT name, room, floor, hostel, fb, det from club where name=%s;',[ str(club) ])
	results=cursor.fetchall()
	dat=[]
	i=0
	for j in range(0, len(results)):
		dat.append(results[j] + ("./temp/img" + str(results[j][0]) + ".jpg" , ))
	data=tuple(dat)
	cursor.execute('SELECT first_name, username from auth_user where club=%s and post=%s;',[str(club),"Club Secretary"])
	secy=cursor.fetchall()
	cursor.execute('SELECT first_name, username from auth_user where club=%s and post=%s;',[str(club),"Joint Secretary"])
	jsecy=cursor.fetchall()
	allow=0
	if request.user.is_staff:
		for i in secy:
			if userid==i[1]:
				allow=1
		for i in jsecy:
			if userid==i[1]:
				allow=1
	cursor.execute('SELECT image, idcw from clubworks where club=%s;',[ str(club) ])
	res=cursor.fetchall()
	for i in range(0, len(res)):
		try:
			write_file(res[i][0], './static/temp/img'+str(res[i][1])+'.jpg')
		except:
			pass
	cursor.execute('SELECT idcw, name, club, date_time from clubworks where club=%s order by date_time DESC;',[ str(club) ])
	res=cursor.fetchall()
	rcw=[]
	i=0
	for j in range(0, len(res)):
		rcw.append(res[j] + ("./temp/img" + str(res[j][0]) + ".jpg" , ))
	cw=tuple(rcw)
	if request.method=="POST":
		room=request.POST.get("room")
		floor=request.POST.get("floor")
		hostel=request.POST.get("hostel")
		fb=request.POST.get("fb")
		det=request.POST.get("det")
		logo=request.FILES['logo'].read()
		cursor = connection.cursor()
		cursor.execute('UPDATE club set logo=%s, room=%s, floor=%s, hostel=%s, fb=%s, det=%s where name=%s;',[str(logo), str(room), str(floor), str(hostel), str(fb), str(det), (str(club))] )
		messages.error(request, 'Updated Successfully')
		return HttpResponseRedirect(reverse('Indian Music Club'))
	return render(request, 'club.html', {'uid':userid, 'frm':"/IndianMusicClub/", 'data':data, 'color':color, 'secy':secy, 'jsecy':jsecy, 'allow':allow, 'cw':cw})

def dfz(request):
	userid=request.user.username
	club="Dance Freakz"
	color="rgb(251, 161, 30)"
	cursor=connection.cursor()
	cursor.execute('SELECT logo, name from club where name=%s;',[ str(club) ])
	results=cursor.fetchall()
	for i in range(0, len(results)):
		try:
			write_file(results[i][0], './static/temp/img'+str(results[i][1])+'.jpg')
		except:
			pass
	cursor.execute('SELECT name, room, floor, hostel, fb, det from club where name=%s;',[ str(club) ])
	results=cursor.fetchall()
	dat=[]
	i=0
	for j in range(0, len(results)):
		dat.append(results[j] + ("./temp/img" + str(results[j][0]) + ".jpg" , ))
	data=tuple(dat)
	cursor.execute('SELECT first_name, username from auth_user where club=%s and post=%s;',[str(club),"Club Secretary"])
	secy=cursor.fetchall()
	cursor.execute('SELECT first_name, username from auth_user where club=%s and post=%s;',[str(club),"Joint Secretary"])
	jsecy=cursor.fetchall()
	allow=0
	if request.user.is_staff:
		for i in secy:
			if userid==i[1]:
				allow=1
		for i in jsecy:
			if userid==i[1]:
				allow=1
	cursor.execute('SELECT image, idcw from clubworks where club=%s;',[ str(club) ])
	res=cursor.fetchall()
	for i in range(0, len(res)):
		try:
			write_file(res[i][0], './static/temp/img'+str(res[i][1])+'.jpg')
		except:
			pass
	cursor.execute('SELECT idcw, name, club, date_time from clubworks where club=%s order by date_time DESC;',[ str(club) ])
	res=cursor.fetchall()
	rcw=[]
	i=0
	for j in range(0, len(res)):
		rcw.append(res[j] + ("./temp/img" + str(res[j][0]) + ".jpg" , ))
	cw=tuple(rcw)
	if request.method=="POST":
		room=request.POST.get("room")
		floor=request.POST.get("floor")
		hostel=request.POST.get("hostel")
		fb=request.POST.get("fb")
		det=request.POST.get("det")
		logo=request.FILES['logo'].read()
		cursor = connection.cursor()
		cursor.execute('UPDATE club set logo=%s, room=%s, floor=%s, hostel=%s, fb=%s, det=%s where name=%s;',[str(logo), str(room), str(floor), str(hostel), str(fb), str(det), (str(club))] )
		messages.error(request, 'Updated Successfully')
		return HttpResponseRedirect(reverse('Dance Freakz'))
	return render(request, 'club.html', {'uid':userid, 'frm':"/DanceFreakz/", 'data':data, 'color':color, 'secy':secy, 'jsecy':jsecy, 'allow':allow, 'cw':cw})

def lit(request):
	userid=request.user.username
	club="Literary Club"
	color="rgb(239, 51, 93)"
	cursor=connection.cursor()
	cursor.execute('SELECT logo, name from club where name=%s;',[ str(club) ])
	results=cursor.fetchall()
	for i in range(0, len(results)):
		try:
			write_file(results[i][0], './static/temp/img'+str(results[i][1])+'.jpg')
		except:
			pass
	cursor.execute('SELECT name, room, floor, hostel, fb, det from club where name=%s;',[ str(club) ])
	results=cursor.fetchall()
	dat=[]
	i=0
	for j in range(0, len(results)):
		dat.append(results[j] + ("./temp/img" + str(results[j][0]) + ".jpg" , ))
	data=tuple(dat)
	cursor.execute('SELECT first_name, username from auth_user where club=%s and post=%s;',[str(club),"Club Secretary"])
	secy=cursor.fetchall()
	cursor.execute('SELECT first_name, username from auth_user where club=%s and post=%s;',[str(club),"Joint Secretary"])
	jsecy=cursor.fetchall()
	allow=0
	if request.user.is_staff:
		for i in secy:
			if userid==i[1]:
				allow=1
		for i in jsecy:
			if userid==i[1]:
				allow=1
	cursor.execute('SELECT image, idcw from clubworks where club=%s;',[ str(club) ])
	res=cursor.fetchall()
	for i in range(0, len(res)):
		try:
			write_file(res[i][0], './static/temp/img'+str(res[i][1])+'.jpg')
		except:
			pass
	cursor.execute('SELECT idcw, name, club, date_time from clubworks where club=%s order by date_time DESC;',[ str(club) ])
	res=cursor.fetchall()
	rcw=[]
	i=0
	for j in range(0, len(res)):
		rcw.append(res[j] + ("./temp/img" + str(res[j][0]) + ".jpg" , ))
	cw=tuple(rcw)
	if request.method=="POST":
		room=request.POST.get("room")
		floor=request.POST.get("floor")
		hostel=request.POST.get("hostel")
		fb=request.POST.get("fb")
		det=request.POST.get("det")
		logo=request.FILES['logo'].read()
		cursor = connection.cursor()
		cursor.execute('UPDATE club set logo=%s, room=%s, floor=%s, hostel=%s, fb=%s, det=%s where name=%s;',[str(logo), str(room), str(floor), str(hostel), str(fb), str(det), (str(club))] )
		messages.error(request, 'Updated Successfully')
		return HttpResponseRedirect(reverse('Literary Club'))
	return render(request, 'club.html', {'uid':userid, 'frm':"/LiteraryClub/", 'data':data, 'color':color, 'secy':secy, 'jsecy':jsecy, 'allow':allow, 'cw':cw})

def addclubwork(request):
	userid=request.user.username
	cursor=connection.cursor()
	cursor.execute('SELECT club from auth_user where username=%s;',[ str(userid) ])
	results=cursor.fetchone()
	club=results[0].strip()
	if request.method=="POST":
		name=request.POST.get("name")
		image=request.FILES['image'].read()
		cursor = connection.cursor()
		cursor.execute('INSERT into clubworks (name, image, club, date_time) values (%s, %s, %s, %s);',(str(name), str(image), str(club), str(datetime.now())))
		messages.error(request, 'Uploaded Successfully')
		return HttpResponseRedirect(reverse('addclubwork'))
	return render(request, 'addclubwork.html', {'uid':userid})

def dashboard(request):
	userid=request.user.username
	data=[]
	cursor = connection.cursor()
	cursor.execute('SELECT * from auth_user where username="%s"; '%(str(userid) ))
	data = cursor.fetchall()
	return render(request, 'dashboard.html', {'uid':userid, 'fbdata':data})

def editprofile(request):
	userid=request.user.username
	if request.method=="POST":
		name=request.POST.get("name")
		email=request.POST.get("email")
		psw1=request.POST.get("psw1")
		psw2=request.POST.get("psw2")
		mob=request.POST.get("mob")
		branch=request.POST.get("branch")
		batch=request.POST.get("batch")
		if int(batch)<=int(datetime.now().year):
			post="Alumini"
		else:
			post="Participant"
		alph="abcdefghijklmnopqrstuvwxyz ABCDEFGHIJKLMNOPQRSTUVWXYZ"
		digit="0123456789_"
		if len(psw1)<8:
			messages.error(request, 'The password should have atleast 8 characters.')
			return HttpResponseRedirect(reverse('editprofile'))
		if psw1!=psw2:
			messages.error(request, 'The password is not same in both fields.')
			return HttpResponseRedirect(reverse('editprofile'))
		passwrd=make_password(psw1)
		flag=True
		for i in name:
			if i not in alph:
				flag=False
		if flag==False:
			messages.error(request, 'Name should contain only letters')
			return HttpResponseRedirect(reverse('editprofile'))
		flag=True
		if '@' not in email:
			flag=False
		if '.' not in email:
			flag=False
		if flag==False:
			messages.error(request, 'Enter proper email address')
			return HttpResponseRedirect(reverse('editprofile'))
		flag=True
		for i in mob:
			if i>'9' or i<'0':
				flag=False
			if i not in digit:
				flag=False
		if len(mob)!=10 or flag==False:
			messages.error(request, 'Enter correct mob no.')
			return HttpResponseRedirect(reverse('editprofile'))
		flag=True
		for i in batch:
			if i not in digit:
				flag=False
		if len(batch)!=4 or flag==False:
			messages.error(request, 'Enter correct batch')
			return HttpResponseRedirect(reverse('editprofile'))
		cursor = connection.cursor()
		cursor.execute('Update auth_user set password="%s", first_name="%s", email="%s", branch="%s", club=NULL, mob="%s", batch="%d", post="%s" where username="%s";'%(str(passwrd),  str(name), str(email), str(branch), str(mob), int(batch), str(post), str(userid) ))
		messages.error(request, 'Profile Updated Successfully')
		return HttpResponseRedirect(reverse('dashboard'))
	return render(request, 'editprofile.html', {'uid':userid} )

def sponsors(request):
	userid=request.user.username
	cursor=connection.cursor()
	cursor.execute('SELECT logo, idpic from sponsors')
	results=cursor.fetchall()
	for i in range(0, len(results)):
		try:
			write_file(results[i][0], './static/temp/img'+str(results[i][1])+'.jpg')
		except:
			pass
	cursor.execute('SELECT idpic, sname, address, mailid, mob from sponsors')
	results=cursor.fetchall()
	dat=[]
	for j in range(0, len(results)):
		dat.append(results[j] + ("./temp/img" + str(results[j][0]) + ".jpg" , ))
	data=tuple(dat)
	if request.method=="POST":
		sname=request.POST.get("sname")
		email=request.POST.get("email")
		pname=request.POST.get("pname")
		post=request.POST.get("post")
		mob=request.POST.get("mob")
		address=request.POST.get("address")
		logo=request.FILES['logo'].read()
		alph="abcdefghijklmnopqrstuvwxyz ABCDEFGHIJKLMNOPQRSTUVWXYZ"
		digit="0123456789_"
		flag=True
		for i in sname:
			if i not in alph:
				flag=False
		if flag==False:
			messages.error(request, 'Name should contain only letters')
			return HttpResponseRedirect(reverse('sponsors'))
		flag=True
		for i in pname:
			if i not in alph:
				flag=False
		if flag==False:
			messages.error(request, 'Name should contain only letters')
			return HttpResponseRedirect(reverse('sponsors'))
		flag=True
		if '@' not in email:
			flag=False
		if '.' not in email:
			flag=False
		if flag==False:
			messages.error(request, 'Enter proper email address')
			return HttpResponseRedirect(reverse('sponsors'))
		flag=True
		for i in mob:
			if i>'9' or i<'0':
				flag=False
			if i not in digit:
				flag=False
		if len(mob)!=10 or flag==False:
			messages.error(request, 'Enter correct mob no.')
			return HttpResponseRedirect(reverse('sponsors'))
		cursor = connection.cursor()
		cursor.execute('INSERT into sponsors (sname, mailid, logo, pname, post, mob, address) values (%s, %s, %s, %s, %s, %s, %s);',(str(sname), str(email), str(logo), str(pname), str(post), str(mob), str(address) ))
		messages.error(request, 'Uploaded Successfully')
		return HttpResponseRedirect(reverse('sponsors'))
	return render(request, 'sponsors.html', {'uid':userid, 'data':data})

def merchandise(request):
	userid=request.user.username
	cursor=connection.cursor()
	cursor.execute('SELECT image, idmerch from merchandise')
	results=cursor.fetchall()
	for i in range(0, len(results)):
		try:
			write_file(results[i][0], './static/temp/img'+str(results[i][1])+'.jpg')
		except:
			pass
	cursor.execute('SELECT idmerch, name, price, typed from merchandise')
	results=cursor.fetchall()
	dat=[]
	i=0
	for j in range(0, len(results)):
		dat.append(results[j] + ("./temp/img" + str(results[j][0]) + ".jpg" , ))
	data=tuple(dat)
	if request.method=="POST":
		if not request.user.is_authenticated():
			messages.error(request, 'Login/ Signup to place order')
			return HttpResponseRedirect(reverse('merchandise'))
		cart=request.POST.getlist("cart")
		if not cart:
			messages.error(request, 'Select atleast one item to place order')
			return HttpResponseRedirect(reverse('merchandise'))
		cursor = connection.cursor()
		total=0
		for i in cart:
			cursor.execute('SELECT price from merchandise where idmerch=%s;',(i.strip()))
			x=cursor.fetchone()
			total = total + int(x[0])
		return render(request, 'order.html', {'uid':userid, 'total':total})
	return render(request, 'merchandise.html', {'uid':userid, 'data':data})

def addmerch(request):
	userid=request.user.username
	if request.method=="POST":
		name=request.POST.get("name")
		price=request.POST.get("price")
		typed=request.POST.get("typed")
		club=request.POST.get("club")
		image=request.FILES['image'].read()
		digit="0123456789"
		flag=True
		for i in price:
			if i not in digit:
				flag=False
		if flag==False:
			messages.error(request, 'Enter correct price')
			return HttpResponseRedirect(reverse('addmerch'))
		cursor = connection.cursor()
		cursor.execute('INSERT into merchandise (name, image, price, typed, club) values (%s, %s, %s, %s, %s);',(str(name), str(image), price, str(typed), str(club) ))
		messages.error(request, 'Uploaded Successfully')
		return HttpResponseRedirect(reverse('merchandise'))
	return render(request, 'addmerch.html', {'uid':userid})

def logout(request):
	if request.user.is_authenticated():
		auth.logout(request)
		messages.success(request, 'Successfully logged out.')
	return HttpResponseRedirect(reverse('login'))