#!/home/stepsizestrategies/.local/bin/python3
# -*- coding: utf-8 -*-

from strategies.forms import LoginForm, RegisterForm
from django.shortcuts import render,redirect

from django.contrib.auth import authenticate, login, logout

from django.utils.html import escape
from math import *
from matplotlib import pyplot
import matplotlib as mpl
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
from matplotlib import pyplot
import mpl_toolkits.mplot3d.axes3d as p3
from matplotlib import animation
import numpy
from random import randint
import xlwt
from sympy import sympify, Symbol, lambdify, Derivative, pi, exp, sin, cos, tan, cot, log, sqrt, Matrix, power
from django.contrib import messages


simulations_list = [ ['picardcl', 'Step Size Strategies Based on Picard Theorem'],
                      ['hatanalizicl', 'Step Size Strategy Based on Error Analysis'],
                      ['pihatacl','Step Size Strategey Based on Picard Theorem and Error Analysis'],

                    ['sisalgocl1', ' Step Size Strategy for The Numerical Integration of Systems of Linear Differential Equations'],
                    ['nonsisalgocl1', ' Step Size Strategy for The Numerical Integration of Systems of Non-Linear Differential Equations'],

                  ]
calculations_list = [ ['picardclf', 'Step Size Strategies Based on Picard Theorem'],
                      ['hatanaliziclf', 'Step Size Strategy Based on Error Analysis'],
                      ['pihataclf','Step Size Strategey Based on Picard Theorem and Error Analysis'],

                    ['sisalgoclf1', ' Step Size Strategy for The Numerical Integration of Systems of Linear Differential Equations'],
                    ['nonsisalgoclf1', ' Step Size Strategy for The Numerical Integration of Systems of Non-Linear Differential Equations'],

                  ]


strategies_list=[  ['picard', 'Step Size Strategies Based on Picard Theorem'],
                   ['hatanalizi', 'Step Size Strategy Based on Error Analysis'],
                   ['pihata','Step Size Strategey Based on Picard Theorem and Error Analysis'],
                   ['sisalgo1', ' Step Size Strategy for The Numerical Integration of Systems of Linear Differential Equations'],
                  ['nonsisalgo1', ' Step Size Strategy for The Numerical Integration of Systems of Non-Linear Differential Equations'],
                ]

iletisims_list=[['Ersan ERDEM', 'ersanerdem.ee@gmail.com'],
               ['Gülnur ÇELİK KIZILKAN', 'gckizilkan@erbakan.edu.tr' ],
               ['Ali Osman ÇIBIKDİKEN','aocdiken@erbakan.edu.tr' ],
               ]

strategies = [  ['Strategies',strategies_list],]

simulations=[  ['Simulations',simulations_list],]

calculations=[  ['Calculations',calculations_list],]

iletisims=[['Contact',iletisims_list],]


def index(request):

    return  render(request, 'graphics/index.html', {'iletisims':iletisims, 'simulations':simulations ,'calculations':calculations,'calculations_list':calculations_list, 'strategies': strategies,'simulations_list':simulations_list, 'strategies_list': strategies_list})



def picard(request):

    return  render(request, 'graphics/picard.html', {'iletisims':iletisims,'calculations':calculations,'calculations_list':calculations_list, 'simulations':simulations , 'strategies': strategies,'simulations_list':simulations_list, 'strategies_list': strategies_list})

def strategiess(request):
    return  render(request, 'graphics/strategiess.html', {'iletisims':iletisims,'calculations':calculations,'calculations_list':calculations_list, 'simulations':simulations , 'strategies': strategies,'simulations_list':simulations_list, 'strategies_list': strategies_list})

def hatanalizi(request):

    return  render(request, 'graphics/hatanalizi.html', {'iletisims':iletisims,'calculations':calculations,'calculations_list':calculations_list, 'simulations':simulations , 'strategies': strategies,'simulations_list':simulations_list, 'strategies_list': strategies_list})

def pihata(request):

    return  render(request, 'graphics/pihata.html', {'iletisims':iletisims,'calculations':calculations,'calculations_list':calculations_list, 'simulations':simulations , 'strategies': strategies,'simulations_list':simulations_list, 'strategies_list': strategies_list})
def sisalgo1(request):

    return  render(request, 'graphics/sisalgo1.html',{'iletisims':iletisims,'calculations':calculations,'calculations_list':calculations_list, 'simulations':simulations , 'strategies': strategies,'simulations_list':simulations_list, 'strategies_list': strategies_list})


def nonsisalgo1(request):

    return  render(request, 'graphics/nonsisalgo1.html', {'iletisims':iletisims,'calculations':calculations,'calculations_list':calculations_list, 'simulations':simulations , 'strategies': strategies,'simulations_list':simulations_list, 'strategies_list': strategies_list})
def about(request):

    return  render(request, 'graphics/about.html', {'iletisims':iletisims,'calculations':calculations,'calculations_list':calculations_list, 'simulations':simulations , 'strategies': strategies,'simulations_list':simulations_list, 'strategies_list': strategies_list})

def login_view(request):
    form = LoginForm(request.POST or None)
    if form.is_valid():
        username = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password')
        user = authenticate(username=username, password=password)
        login(request, user)

        return redirect('index')

    return render(request, 'graphics/login.html', {"form": form, 'title': 'Login','iletisims':iletisims,'calculations':calculations,'calculations_list':calculations_list, 'simulations':simulations , 'strategies': strategies,'simulations_list':simulations_list, 'strategies_list': strategies_list})


def register_view(request):
    form = RegisterForm(request.POST or None)
    if form.is_valid():
        user = form.save()
        password = form.cleaned_data.get('password')
        user.set_password(password)
        # user.is_staff = user.is_superuser = True
        user.save()
        new_user = authenticate(username=user.username, password=password)
        login(request, new_user)
        return redirect('index')

    return render(request, 'graphics/register.html', { 'title': 'Register','iletisims':iletisims,'calculations':calculations,'calculations_list':calculations_list, 'simulations':simulations , 'strategies': strategies,'simulations_list':simulations_list, 'strategies_list': strategies_list})


def logout_view(request):
    logout(request)
    return redirect('login')

def hatanalizicl(request):
     mycache = randint(1000, 10000)
     out=open("strategies/templates/textfiles/hatanalizicl.txt","w")
     out.write("$i        h_{i}          t_{i}          y_{i}$\n")

     mycache = randint(1000, 10000)
     tl=[]
     xl=[]
     hl=[]
     Ml=[]
     al=[]
     try:
         mycache = randint(1000, 10000)
         t=Symbol('t')
         x=Symbol('x')
         expr=sympify(request.POST['f'])

         v=lambdify((t,x),expr)

         def f(t1,x1):
             return v(t1,x1)

         expr2=(Derivative(expr,x).doit())*expr+Derivative(expr,t).doit()

         df=lambdify((t,x),expr2)



         hp=float(request.POST['hp'])
         t0=float(escape(request.POST['t0']))
         tl.append(t0)
         x0=float(escape(request.POST['x0']))
         xl.append(x0)
         a=float(escape(request.POST['a']))
         b=float(escape(request.POST['b']))
         dlt=float(escape(request.POST['d']))
         i=0;
         while tl[i]<t0+a:
              alf=numpy.linspace(tl[i]-a,tl[i]+a)
              bet=numpy.linspace(xl[i]-b,xl[i]+b)
              func=numpy.vectorize(df)
              M=numpy.max(abs(func(alf,bet)))
              Ml.append(M)
              h=numpy.sqrt(2*dlt/Ml[i])
              hl.append(h)
              if sum(hl[:i])+hl[i]<=a:
                  if hl[i]>hp:
                     hl[i]=hl[i]
                     t=tl[i]+hl[i]
                     x=xl[i]+hl[i]*f(tl[i],xl[i])
                     tl.append(t)
                     xl.append(x)
                     out.write("{:d}   {:.6f}    {:.6f}    {:.6f}\n".format(i,hl[i],tl[i],xl[i]))
              else:
                  if hl[i]>hp:
                      hl[i]=a-sum(hl[:i])
                      t=tl[i]+hl[i]
                      x=xl[i]+hl[i]*f(tl[i],xl[i])
                      tl.append(t)
                      xl.append(x)
                      out.write("{:d}   {:.6f}    {:.6f}    {:.6f}\n".format(i,hl[i],tl[i],xl[i]))
              if hl[i]<hp:
                   hl[i]=0
                   break;
              i+=1
         for k in range(len(hl)):
             al.append(k)


         pyplot.grid(linewidth=0.35,linestyle='-')
         pyplot.plot(tl,xl,'gs',linewidth=3)
         pyplot.legend([r'$x_{i}$'],fontsize=13)
         pyplot.xlabel(r'$t_{i}$',position=(1.01,-0.12),fontsize=13)
         pyplot.ylabel(r'$x_{i}$',position=(-0.1,1.01), fontsize=13, rotation='horizontal')
         pyplot.title('Numeric Solution')

         pyplot.savefig('strategies/static/graphics/images/hatanalizicl.png')
         pyplot.close()

         pyplot.grid(linewidth=0.35, linestyle='-')
         pyplot.plot(al,hl,'bs' ,linewidth=3)
         pyplot.legend([r'$h_{i}$'],fontsize=13)
         pyplot.xlabel(r'$i$',position=(1.01,-0.12),fontsize=13)
         pyplot.ylabel(r'$h_{i}$',position=(-0.1,1.01), fontsize=13, rotation='horizontal')
         pyplot.title('Step Size')
         pyplot.savefig('strategies/static/graphics/images/errhi.png')
         pyplot.close()
         out.close()

         book = xlwt.Workbook()
         ws = book.add_sheet('Euler Method') # Add a sheet
         excl = open("strategies/templates/textfiles/hatanalizicl.txt", 'r')
         data = excl.readlines() # read all lines at once
         for i in range(len(data)):
             row = data[i].split()  # This will return a line of string data, you may need to convert to other formats depending on your use cas
             for j in range(len(row)):
                 ws.write(i, j, row[j])  # Write to cell i, j
         book.save("strategies/static/excelfiles/hatanalizicl.xls")
         excl.close()


     except:
          mycache = randint(1000, 10000)
     return render(request, 'graphics/hatanalizicl.html', {'calculations':calculations,'calculations_list':calculations_list,'iletisims':iletisims, 'mycache':mycache,'simulations':simulations , 'strategies': strategies,'simulations_list':simulations_list, 'strategies_list': strategies_list})

def hatanaliziclf(request):
     result=[]
     mycache = randint(1000, 10000)
     out=open("strategies/templates/textfiles/hatanalizicl.txt","w")
     out.write("i        hi          ti          yi\n")

     mycache = randint(1000, 10000)
     tl=[]
     xl=[]
     hl=[]
     Ml=[]
     try:
         mycache = randint(1000, 10000)
         t=Symbol('t')
         x=Symbol('x')
         expr=sympify(request.POST['f'])

         v=lambdify((t,x),expr)

         def f(t1,x1):
             return v(t1,x1)

         expr2=(Derivative(expr,x).doit())*expr+Derivative(expr,t).doit()

         df=lambdify((t,x),expr2)



         hp=float(request.POST['hp'])
         expr3=sympify(request.POST['t0'])

         m1=lambdify(t,expr3)
         def a1(t):
             return m1(t)
         t0=float(a1(1))
         tl.append(t0)

         expr4=sympify(request.POST['x0'])

         n1=lambdify(t,expr4)
         def b1(t):
             return n1(t)
         x0=float(b1(1))
         xl.append(x0)


         expr5=sympify(request.POST['a'])

         p1=lambdify(t,expr5)
         def s1(t):
             return p1(t)
         a=float(s1(1))

         expr6=sympify(request.POST['b'])

         z1=lambdify(t,expr6)
         def u1(t):
             return z1(t)
         b=float(u1(1))
         dlt=float(escape(request.POST['d']))
         i=0;
         while tl[i]<t0+a:
              alf=numpy.linspace(tl[i]-a,tl[i]+a)
              bet=numpy.linspace(xl[i]-b,xl[i]+b)
              func=numpy.vectorize(df)
              M=numpy.max(abs(func(alf,bet)))
              Ml.append(M)
              h=numpy.sqrt(2*dlt/Ml[i])
              hl.append(h)
              if sum(hl[:i])+hl[i]<=a:
                  if hl[i]>hp:
                     hl[i]=hl[i]
                     t=tl[i]+hl[i]
                     x=xl[i]+hl[i]*f(tl[i],xl[i])
                     tl.append(t)
                     xl.append(x)
                     tmp={'ite':i,
                          'hi':hl[i],
                          'ti':tl[i],
                          'xi':xl[i]

                         }
                     result.append(tmp)
                     out.write("{:d}   {:.6f}    {:.6f}    {:.6f}\n".format(i,hl[i],tl[i],xl[i]))
              else:
                  if hl[i]>hp:
                      hl[i]=a-sum(hl[:i])
                      t=tl[i]+hl[i]
                      x=xl[i]+hl[i]*f(tl[i],xl[i])
                      tl.append(t)
                      xl.append(x)
                      tmp={'ite':i,
                          'hi':hl[i],
                          'ti':tl[i],
                          'xi':xl[i]

                         }
                      result.append(tmp)
                      out.write("{:d}   {:.6f}    {:.6f}    {:.6f}\n".format(i,hl[i],tl[i],xl[i]))
              if hl[i]<hp:
                   hl[i]=0
                   break;
              i+=1

         out.close()

         book = xlwt.Workbook()
         ws = book.add_sheet('Euler Method') # Add a sheet
         excl = open("strategies/templates/textfiles/hatanalizicl.txt", 'r')
         data = excl.readlines() # read all lines at once
         for i in range(len(data)):
             row = data[i].split()  # This will return a line of string data, you may need to convert to other formats depending on your use cas
             for j in range(len(row)):
                 ws.write(i, j, row[j])  # Write to cell i, j
         book.save("strategies/static/excelfiles/hatanalizicl.xls")
         excl.close()


     except:
          mycache = randint(1000, 10000)
     return render(request, 'graphics/hatanaliziclf.html', {'result':result,'calculations':calculations,'calculations_list':calculations_list,'iletisims':iletisims, 'mycache':mycache,'simulations':simulations , 'strategies': strategies,'simulations_list':simulations_list, 'strategies_list': strategies_list})

def sisalgocl1(request):
     result=[]
     mycache = randint(1000, 10000)
     out=open("strategies/templates/textfiles/sisalgocl1.txt","w")
     out.write("i      hi        ti     ||X(ti)||   ||LEi||    x1(ti)    x2(ti)\n")

     try:
        mycache = randint(1000, 10000)
        N=2

        x11=float(request.POST['x11'])
        x21=float(request.POST['x21'])

        X0=numpy.array([[x11],[x21]])

        a11=float(escape(request.POST['a11']))
        a12=float(escape(request.POST['a12']))
        a21=float(escape(request.POST['a21']))
        a22=float(escape(request.POST['a22']))

        A=numpy.array([[a11,a12],[a21,a22]])

        b=float(escape(request.POST['b']))
        a=float(escape(request.POST['a']))
        t0=float(escape(request.POST['t0']))
        hp=float(escape(request.POST['hp']))
        d=float(escape(request.POST['d']))

        Y0=X0
        N=len(A)
        alfa=numpy.max(numpy.abs(A))
        tl=[t0]
        Yl=[Y0]
        Zl=[Y0]
        betal=[]
        LEl=[]
        hl=[]
        cl=[numpy.linalg.norm(Y0,'fro')]
        l1=[]
        l2=[]
        al=[]
        b1l=[]
        k=0;
        while tl[k]<t0+a:

              bet=numpy.max(b+abs(Yl[k]))
              betal.append(bet)
              h=numpy.sqrt(2*d/betal[k])/(alfa*N**1.25)
              hl.append(h)
              if sum(hl[:k])+hl[k]<=a:
                 if hl[k]>hp:
                    hl[k]=hl[k]
                    t=tl[k]+hl[k]
                    tl.append(t)
                    Y=numpy.add(Yl[k],numpy.dot(hl[k]*A,Yl[k]))
                    Yl.append(Y)
                    Z=numpy.dot(numpy.exp(A*hl[k]),Yl[k])
                    Zl.append(Z)
                    LE=numpy.linalg.norm(Zl[k+1]-Yl[k+1],'fro')
                    LEl.append(LE)
                    c=numpy.linalg.norm(Yl[k+1], 'fro')
                    cl.append(c)
                    l1.append(Yl[k][0][0])
                    l2.append(Yl[k][1][0])
                    tmp = {
                            'ite' : k,
                            'hi': hl[k],
                            'ti': tl[k],
                            'Xti': cl[k],
                            'LEi': LEl[k],
                            'x1ti': l1[k],
                            'x2ti': l2[k]
                        }
                    result.append(tmp)
                    out.write("{:d}   {:.6f}  {:.6f}  {:.6f}  {:.6f}    {:.6f}  {:.6f}\n".format(k,hl[k],tl[k],cl[k],LEl[k],l1[k],l2[k]))

              else:
                  if hl[k]>hp:
                     hl[k]=a-sum(hl[:k])

                     t=tl[k]+hl[k]
                     tl.append(t)
                     Y=numpy.add(Yl[k],numpy.dot(hl[k]*A,Yl[k]))
                     Yl.append(Y)
                     Z=numpy.dot(numpy.exp(A*hl[k]),Yl[k])
                     Zl.append(Z)
                     LE=numpy.linalg.norm(Zl[k+1]-Yl[k+1],'fro')
                     LEl.append(LE)
                     c=numpy.linalg.norm(Yl[k+1], 'fro')
                     cl.append(c)
                     l1.append(Yl[k][0][0])
                     l2.append(Yl[k][1][0])
                     tmp = {
                            'ite' : k,
                            'hi': hl[k],
                            'ti': tl[k],
                            'Xti': cl[k],
                            'LEi': LEl[k],
                            'x1ti': l1[k],
                            'x2ti': l2[k]
                        }
                     result.append(tmp)
                     out.write("{:d}   {:.6f}  {:.6f}  {:.6f}  {:.6f}    {:.6f}  {:.6f}\n".format(k,hl[k],tl[k],cl[k],LEl[k],l1[k],l2[k]))
              if hl[k]<hp:
                   hl[k]=0
                   break;

              k+=1










        for k in range(len(hl)):
            al.append(k)

        for i in range(len(l1)):
            out.write("{:.6f}   {:.6f}\n".format(tl[i],l1[i]))
        ye=[]
        for i in range(len(tl)-1):
            ye.append(tl[i])

        pyplot.figure(1)
        pyplot.grid(linestyle='-')
        pyplot.plot(tl,cl,'gs', linewidth=3)
        pyplot.legend([r'$||X_{i}||$'],fontsize=13)
        pyplot.ylabel(r'$||X_{i}||$',position=(-0.1,1.01), fontsize=13, rotation='horizontal')
        pyplot.xlabel(r'$t_{i}$',position=(1.01,-0.12),fontsize=13)
        pyplot.title('Norm of Numeric Solution')
        pyplot.savefig('strategies/static/graphics/images/sisalgocl1.png')
        pyplot.close()


        pyplot.figure(2)
        pyplot.grid()
        pyplot.plot(al,hl,'bs' ,linewidth=3)
        pyplot.legend([r'$h_{i}$'],fontsize=13)
        pyplot.xlabel(r'$i$',position=(1.01,-0.12),fontsize=13)
        pyplot.ylabel(r'$h_{i}$',position=(-0.1,1.01), fontsize=13, rotation='horizontal')
        pyplot.title('Step Size')
        pyplot.savefig('strategies/static/graphics/images/sisalgohi.png')
        pyplot.close()


        pyplot.figure(3)
        pyplot.grid()
        pyplot.plot(ye,l1,'cs' ,linewidth=3)
        pyplot.legend([r'$x_{i}$'],fontsize=13)
        pyplot.xlabel(r'$t_{i}$',position=(1.01,-0.12),fontsize=13)
        pyplot.ylabel(r'$x_{i}$',position=(-0.1,1.01), fontsize=13, rotation='horizontal')
        pyplot.title('First Component')
        pyplot.savefig('strategies/static/graphics/images/sisx1.png')
        pyplot.close()

        pyplot.figure(4)
        pyplot.grid()
        pyplot.plot(ye,l2,'ms' ,linewidth=3)
        pyplot.legend([r'$y_{i}$'],fontsize=13)
        pyplot.xlabel(r'$t_{i}$',position=(1.01,-0.12),fontsize=13)
        pyplot.ylabel(r'$y_{i}$',position=(-0.1,1.01), fontsize=13, rotation='horizontal')
        pyplot.title('Second Component')
        pyplot.savefig('strategies/static/graphics/images/sisx2.png')
        pyplot.close()

        pyplot.figure(5)
        pyplot.grid()
        pyplot.plot(al,LEl,'rs' ,linewidth=3)
        pyplot.legend([r'$||LE_{i}||$'],fontsize=13)
        pyplot.xlabel(r'$i$',position=(1.01,-0.12),fontsize=13)
        pyplot.ylabel(r'$||LE_{i}||$',position=(-0.1,1.01), fontsize=13, rotation='horizontal')
        pyplot.title('Local Error')
        pyplot.savefig('strategies/static/graphics/images/sisle.png')
        pyplot.close()



        out.close()
        book = xlwt.Workbook()
        ws = book.add_sheet('Euler Method') # Add a sheet
        excl = open("strategies/templates/textfiles/sisalgocl1.txt", 'r')
        data = excl.readlines() # read all lines at once
        for i in range(len(data)):
            row = data[i].split()  # This will return a line of string data, you may need to convert to other formats depending on your use cas
            for j in range(len(row)):
                ws.write(i, j, row[j])  # Write to cell i, j
        book.save("strategies/static/excelfiles/sisalgocl1.xls")
        excl.close()




     except:
          mycache = randint(1000, 10000)
     return render(request, 'graphics/sisalgocl1.html', {'calculations':calculations,'calculations_list':calculations_list,'result':result, 'mycache':mycache,'iletisims':iletisims, 'simulations':simulations , 'strategies': strategies,'simulations_list':simulations_list, 'strategies_list': strategies_list})

def sisalgocl2(request):

     mycache = randint(1000, 10000)


     try:
        mycache = randint(1000, 10000)


        x11=float(request.POST['x11'])
        x21=float(request.POST['x21'])
        x31=float(request.POST['x31'])

        X0=numpy.array([[x11],[x21],[x31]])

        a11=float(escape(request.POST['a11']))
        a12=float(escape(request.POST['a12']))
        a13=float(escape(request.POST['a13']))
        a21=float(escape(request.POST['a21']))
        a22=float(escape(request.POST['a22']))
        a23=float(escape(request.POST['a23']))
        a31=float(escape(request.POST['a31']))
        a32=float(escape(request.POST['a32']))
        a33=float(escape(request.POST['a33']))

        A=numpy.array([[a11,a12,a13],[a21,a22,a23],[a31,a32,a33]])

        b=float(escape(request.POST['b']))
        a=float(escape(request.POST['a']))
        t0=float(escape(request.POST['t-0-0']))
        hp=float(escape(request.POST['hp']))
        d=float(escape(request.POST['d']))

        Y0=X0
        N=len(A)
        alfa=numpy.max(numpy.abs(A))
        tl=[t0]
        Yl=[Y0]
        Zl=[Y0]
        betal=[]
        LEl=[]
        hl=[]
        cl=[numpy.linalg.norm(Y0,'fro')]
        l1=[]
        l2=[]
        al=[]
        l3=[]
        k=0;
        while tl[k]<t0+a:

              bet=numpy.max(b+abs(Yl[k]))
              betal.append(bet)
              h=numpy.sqrt(2*d/betal[k])/(alfa*N**1.25)
              hl.append(h)
              if sum(hl[:k])+hl[k]<=a:
                 if hl[k]>hp:
                    hl[k]=hl[k]
                    t=tl[k]+hl[k]
                    tl.append(t)
                    Y=numpy.add(Yl[k],numpy.dot(hl[k]*A,Yl[k]))
                    Yl.append(Y)
                    Z=numpy.dot(numpy.exp(A*hl[k]),Yl[k])
                    Zl.append(Z)
                    LE=numpy.linalg.norm(Zl[k+1]-Yl[k+1],'fro')
                    LEl.append(LE)
                    c=numpy.linalg.norm(Yl[k+1], 'fro')
                    cl.append(c)
                    l1.append(Yl[k][0][0])
                    l2.append(Yl[k][1][0])
                    l3.append(Yl[k][2][0])

              else:
                  if hl[k]>hp:
                     hl[k]=a-sum(hl[:k])

                     t=tl[k]+hl[k]
                     tl.append(t)
                     Y=numpy.add(Yl[k],numpy.dot(hl[k]*A,Yl[k]))
                     Yl.append(Y)
                     Z=numpy.dot(numpy.exp(A*hl[k]),Yl[k])
                     Zl.append(Z)
                     LE=numpy.linalg.norm(Zl[k+1]-Yl[k+1],'fro')
                     LEl.append(LE)
                     c=numpy.linalg.norm(Yl[k+1], 'fro')
                     cl.append(c)
                     l1.append(Yl[k][0][0])
                     l2.append(Yl[k][1][0])
                     l3.append(Yl[k][2][0])

              if hl[k]<hp:
                   hl[k]=0
                   break;

              k+=1










        for k in range(len(hl)):
            al.append(k)


        ye=[]
        for i in range(len(tl)-1):
            ye.append(tl[i])

        pyplot.figure(1)
        pyplot.grid()
        pyplot.plot(tl,cl,'gs', linewidth=3)
        pyplot.legend([r'$||X_{i}||$'],fontsize=13)
        pyplot.ylabel(r'$||X_{i}||$',position=(-0.1,1.01), fontsize=13, rotation='horizontal')
        pyplot.xlabel(r'$t_{i}$',position=(1.01,-0.12),fontsize=13)
        pyplot.title('Norm of Numeric Solution')
        pyplot.savefig('strategies/static/graphics/images/sisalgocl1.png')
        pyplot.close()


        pyplot.figure(2)
        pyplot.grid()
        pyplot.plot(al,hl,'bs' ,linewidth=3)
        pyplot.legend([r'$h_{i}$'], fontsize=13)
        pyplot.xlabel(r'$i$',position=(1.01,-0.12),fontsize=13)
        pyplot.ylabel(r'$h_{i}$',position=(-0.1,1.01), fontsize=13, rotation='horizontal')
        pyplot.title('Step Size')
        pyplot.savefig('strategies/static/graphics/images/sisalgohi.png')
        pyplot.close()


        pyplot.figure(3)
        pyplot.grid()
        pyplot.plot(ye,l1,'cs' ,linewidth=3)
        pyplot.legend([r'$x_{i}$'], fontsize=13)
        pyplot.xlabel(r'$t_{i}$', position=(1.01,-0.12),fontsize=13)
        pyplot.ylabel(r'$x_{i}$',position=(-0.1,1.01), fontsize=13, rotation='horizontal')
        pyplot.title('First Component')
        pyplot.savefig('strategies/static/graphics/images/sisx1.png')
        pyplot.close()

        pyplot.figure(4)
        pyplot.grid()
        pyplot.plot(ye,l2,'ms' ,linewidth=3)
        pyplot.legend([r'$y_{i}$'], fontsize=13)
        pyplot.xlabel(r'$t_{i}$',position=(1.01,-0.12),fontsize=13)
        pyplot.ylabel(r'$y_{i}$',position=(-0.1,1.01), fontsize=13, rotation='horizontal')
        pyplot.title('Second Component')
        pyplot.savefig('strategies/static/graphics/images/sisx2.png')
        pyplot.close()

        pyplot.grid(5)
        pyplot.plot(ye,l3,'ks' ,linewidth=3)
        pyplot.legend([r'$z_{i}$'], fontsize=13)
        pyplot.xlabel(r'$t_{i}$',position=(1.01,-0.12),fontsize=13)
        pyplot.ylabel(r'$z_{i}$',position=(-0.1,1.01), fontsize=13, rotation='horizontal')
        pyplot.title('Third Component')
        pyplot.savefig('strategies/static/graphics/images/sisx3.png')
        pyplot.close()



     except:
          mycache = randint(1000, 10000)
     return render(request, 'graphics/sisalgocl2.html', {'calculations':calculations,'calculations_list':calculations_list, 'mycache':mycache,'iletisims':iletisims, 'simulations':simulations , 'strategies': strategies,'simulations_list':simulations_list, 'strategies_list': strategies_list})

def sisalgocl3(request):

     mycache = randint(1000, 10000)


     try:
        mycache = randint(1000, 10000)


        x11=float(request.POST['x11'])
        x21=float(request.POST['x21'])
        x31=float(request.POST['x31'])
        x41=float(request.POST['x41'])


        X0=numpy.array([[x11],[x21],[x31],[x41]])

        a11=float(escape(request.POST['a11']))
        a12=float(escape(request.POST['a12']))
        a13=float(escape(request.POST['a13']))
        a14=float(escape(request.POST['a14']))

        a21=float(escape(request.POST['a21']))
        a22=float(escape(request.POST['a22']))
        a23=float(escape(request.POST['a23']))
        a24=float(escape(request.POST['a24']))

        a31=float(escape(request.POST['a31']))
        a32=float(escape(request.POST['a32']))
        a33=float(escape(request.POST['a33']))
        a34=float(escape(request.POST['a34']))

        a41=float(escape(request.POST['a41']))
        a42=float(escape(request.POST['a42']))
        a43=float(escape(request.POST['a43']))
        a44=float(escape(request.POST['a44']))








        A=numpy.array([[a11,a12,a13,a14],[a21,a22,a23,a24],[a31,a32,a33,a34],[a41,a42,a43,a44]])

        b=float(escape(request.POST['b']))
        a=float(escape(request.POST['a']))
        t0=float(escape(request.POST['t0']))
        hp=float(escape(request.POST['hp']))
        d=float(escape(request.POST['d']))

        Y0=X0
        N=len(A)
        alfa=numpy.max(numpy.abs(A))
        tl=[t0]
        Yl=[Y0]
        Zl=[Y0]
        betal=[]
        LEl=[]
        hl=[]
        cl=[numpy.linalg.norm(Y0,'fro')]
        l1=[]
        l2=[]
        al=[]
        l3=[]
        l4=[]
        k=0;
        while tl[k]<t0+a:

              bet=numpy.max(b+abs(Yl[k]))
              betal.append(bet)
              h=numpy.sqrt(2*d/betal[k])/(alfa*N**1.25)
              hl.append(h)
              if sum(hl[:k])+hl[k]<=a:
                 if hl[k]>hp:
                    hl[k]=hl[k]
                    t=tl[k]+hl[k]
                    tl.append(t)
                    Y=numpy.add(Yl[k],numpy.dot(hl[k]*A,Yl[k]))
                    Yl.append(Y)
                    Z=numpy.dot(numpy.exp(A*hl[k]),Yl[k])
                    Zl.append(Z)
                    LE=numpy.linalg.norm(Zl[k+1]-Yl[k+1],'fro')
                    LEl.append(LE)
                    c=numpy.linalg.norm(Yl[k+1], 'fro')
                    cl.append(c)
                    l1.append(Yl[k][0][0])
                    l2.append(Yl[k][1][0])
                    l3.append(Yl[k][2][0])
                    l4.append(Yl[k][3][0])

              else:
                  if hl[k]>hp:
                     hl[k]=a-sum(hl[:k])

                     t=tl[k]+hl[k]
                     tl.append(t)
                     Y=numpy.add(Yl[k],numpy.dot(hl[k]*A,Yl[k]))
                     Yl.append(Y)
                     Z=numpy.dot(numpy.exp(A*hl[k]),Yl[k])
                     Zl.append(Z)
                     LE=numpy.linalg.norm(Zl[k+1]-Yl[k+1],'fro')
                     LEl.append(LE)
                     c=numpy.linalg.norm(Yl[k+1], 'fro')
                     cl.append(c)
                     l1.append(Yl[k][0][0])
                     l2.append(Yl[k][1][0])
                     l3.append(Yl[k][2][0])
                     l4.append(Yl[k][3][0])

              if hl[k]<hp:
                   hl[k]=0
                   break;

              k+=1










        for k in range(len(hl)):
            al.append(k)


        ye=[]
        for i in range(len(tl)-1):
            ye.append(tl[i])

        pyplot.figure(1)
        pyplot.grid(linewidth=1)
        pyplot.plot(tl,cl,'gs', linewidth=3)
        pyplot.legend([r'$||X_{i}||$'],fontsize=13)
        pyplot.ylabel(r'$||X_{i}||$',position=(-0.1,1.01), fontsize=13, rotation='horizontal')
        pyplot.xlabel(r'$t_{i}$',position=(1.01,-0.12),fontsize=13)
        pyplot.title('Norm of Numeric Solution')
        pyplot.savefig('strategies/static/graphics/images/sisalgocl1.png')
        pyplot.close()


        pyplot.figure(2)
        pyplot.grid()
        pyplot.plot(al,hl,'bs' ,linewidth=3)
        pyplot.legend([r'$h_{i}$'],fontsize=13)
        pyplot.xlabel(r'$i$',position=(1.01,-0.12),fontsize=13)
        pyplot.ylabel(r'$h_{i}$',position=(-0.1,1.01), fontsize=13, rotation='horizontal')
        pyplot.title('Step Size')
        pyplot.savefig('strategies/static/graphics/images/sisalgohi.png')
        pyplot.close()


        pyplot.figure(3)
        pyplot.grid()
        pyplot.plot(ye,l1,'cs' ,linewidth=3)
        pyplot.legend([r'$x_{i}$'],fontsize=13)
        pyplot.xlabel(r'$t_{i}$',position=(1.01,-0.12),fontsize=13)
        pyplot.ylabel(r'$x_{i}$',position=(-0.1,1.01), fontsize=13, rotation='horizontal')
        pyplot.title('First Component')
        pyplot.savefig('strategies/static/graphics/images/sisx1.png')
        pyplot.close()

        pyplot.figure(4)
        pyplot.grid()
        pyplot.plot(ye,l2,'ms' ,linewidth=3)
        pyplot.legend([r'$y_{i}$'],fontsize=13)
        pyplot.xlabel(r'$t_{i}$',position=(1.01,-0.12),fontsize=13)
        pyplot.ylabel(r'$y_{i}$',position=(-0.1,1.01), fontsize=13, rotation='horizontal')
        pyplot.title('Second Component')
        pyplot.savefig('strategies/static/graphics/images/sisx2.png')
        pyplot.close()

        pyplot.figure(5)
        pyplot.grid()
        pyplot.plot(ye,l3,'ks' ,linewidth=3)
        pyplot.legend([r'$z_{i}$'],fontsize=13)
        pyplot.xlabel(r'$t_{i}$',position=(1.01,-0.12),fontsize=13)
        pyplot.ylabel(r'$z_{i}$',position=(-0.1,1.01), fontsize=13, rotation='horizontal')
        pyplot.title('Third Component')
        pyplot.savefig('strategies/static/graphics/images/sisx3.png')
        pyplot.close()

        pyplot.figure(6)
        pyplot.grid()
        pyplot.plot(ye,l4,'ys' ,linewidth=3)
        pyplot.legend([r'$w_{i}$'],fontsize=13)
        pyplot.xlabel(r'$t_{i}$',position=(1.01,-0.12),fontsize=13)
        pyplot.ylabel(r'$w_{i}$',position=(-0.1,1.01), fontsize=13, rotation='horizontal')
        pyplot.title('Fourth Component')
        pyplot.savefig('strategies/static/graphics/images/sisx4.png')
        pyplot.close()



     except:
          mycache = randint(1000, 10000)
     return render(request, 'graphics/sisalgocl3.html', {'calculations':calculations,'calculations_list':calculations_list, 'mycache':mycache,'iletisims':iletisims, 'simulations':simulations , 'strategies': strategies,'simulations_list':simulations_list, 'strategies_list': strategies_list})








def sisalgoclf1(request):
     result=[]
     mycache = randint(1000, 10000)
     out=open("strategies/templates/textfiles/sisalgocl1.txt","w")
     out.write("i      hi        ti     ||X(ti)||     x1(ti)    x2(ti)\n")

     try:
        mycache = randint(1000, 10000)
        N=2

        x11=float(request.POST['x11'])
        x21=float(request.POST['x21'])

        X0=numpy.array([[x11],[x21]])

        a11=float(escape(request.POST['a11']))
        a12=float(escape(request.POST['a12']))
        a21=float(escape(request.POST['a21']))
        a22=float(escape(request.POST['a22']))

        A=numpy.array([[a11,a12],[a21,a22]])

        b=float(escape(request.POST['b']))
        a=float(escape(request.POST['a']))
        t0=float(escape(request.POST['t0']))
        hp=float(escape(request.POST['hp']))
        d=float(escape(request.POST['d']))

        Y0=X0
        N=len(A)
        alfa=numpy.max(numpy.abs(A))
        tl=[t0]
        Yl=[Y0]
        Zl=[Y0]
        betal=[]
        LEl=[]
        hl=[]
        cl=[numpy.linalg.norm(Y0,'fro')]
        l1=[]
        l2=[]
        al=[]
        b1l=[]
        k=0;
        while tl[k]<t0+a:

              bet=numpy.max(b+abs(Yl[k]))
              betal.append(bet)
              h=numpy.sqrt(2*d/betal[k])/(alfa*N**1.25)
              hl.append(h)
              if sum(hl[:k])+hl[k]<=a:
                 if hl[k]>hp:
                    hl[k]=hl[k]
                    t=tl[k]+hl[k]
                    tl.append(t)
                    Y=numpy.add(Yl[k],numpy.dot(hl[k]*A,Yl[k]))
                    Yl.append(Y)
                    Z=numpy.dot(numpy.exp(A*hl[k]),Yl[k])
                    Zl.append(Z)
                    LE=numpy.linalg.norm(Zl[k+1]-Yl[k+1],'fro')
                    LEl.append(LE)
                    c=numpy.linalg.norm(Yl[k+1], 'fro')
                    cl.append(c)
                    l1.append(Yl[k][0][0])
                    l2.append(Yl[k][1][0])
                    tmp = {
                            'ite' : k,
                            'hi':"{0:.8f}".format( hl[k]),
                            'ti': "{0:.8f}".format(tl[k]),
                            'Xti':"{0:.8f}".format( cl[k]),

                            'x1ti':"{0:.8f}".format( l1[k]),
                            'x2ti': "{0:.8f}".format(l2[k])
                        }
                    result.append(tmp)
                    out.write("{:d}   {:.6f}  {:.6f}  {:.6f}  {:.6f}      {:.6f}\n".format(k,hl[k],tl[k],cl[k],l1[k],l2[k]))

              else:
                  if hl[k]>hp:
                     hl[k]=a-sum(hl[:k])

                     t=tl[k]+hl[k]
                     tl.append(t)
                     Y=numpy.add(Yl[k],numpy.dot(hl[k]*A,Yl[k]))
                     Yl.append(Y)
                     Z=numpy.dot(numpy.exp(A*hl[k]),Yl[k])
                     Zl.append(Z)
                     LE=numpy.linalg.norm(Zl[k+1]-Yl[k+1],'fro')
                     LEl.append(LE)
                     c=numpy.linalg.norm(Yl[k+1], 'fro')
                     cl.append(c)
                     l1.append(Yl[k][0][0])
                     l2.append(Yl[k][1][0])
                     tmp = {
                            'ite' : k,
                            'hi': "{0:.8}".format( hl[k]),
                            'ti': "{0:.8f}".format(tl[k]),
                            'Xti':"{0:.8f}".format( cl[k]),

                            'x1ti':"{0:.8f}".format( l1[k]),
                            'x2ti': "{0:.8f}".format(l2[k])
                        }
                     result.append(tmp)
                     out.write("{:d}   {:.6f}  {:.6f}  {:.6f}    {:.6f}  {:.6f}\n".format(k,hl[k],tl[k],cl[k],l1[k],l2[k]))
              if hl[k]<hp:
                   hl[k]=0
                   break;

              k+=1





        out.close()
        book = xlwt.Workbook()
        ws = book.add_sheet('Euler Method') # Add a sheet
        excl = open("strategies/templates/textfiles/sisalgocl1.txt", 'r')
        data = excl.readlines() # read all lines at once
        for i in range(len(data)):
            row = data[i].split()  # This will return a line of string data, you may need to convert to other formats depending on your use cas
            for j in range(len(row)):
                ws.write(i, j, row[j])  # Write to cell i, j
        book.save("strategies/static/excelfiles/sisalgocl1.xls")
        excl.close()




     except:
          mycache = randint(1000, 10000)
     return render(request, 'graphics/sisalgoclf1.html', {'result':result,'calculations':calculations,'calculations_list':calculations_list,'result':result, 'mycache':mycache,'iletisims':iletisims, 'simulations':simulations , 'strategies': strategies,'simulations_list':simulations_list, 'strategies_list': strategies_list})


def sisalgoclf2(request):
     result=[]
     mycache = randint(1000, 10000)
     out=open("strategies/templates/textfiles/sisalgocl1.txt","w")
     out.write("i      hi        ti     ||X(ti)||   x1(ti)    x2(ti)\n")

     try:
        mycache = randint(1000, 10000)
        N=2
        result=[]

        x11=float(request.POST['x11'])
        x21=float(request.POST['x21'])

        X0=numpy.array([[x11],[x21]])

        a11=float(escape(request.POST['a11']))
        a12=float(escape(request.POST['a12']))
        a21=float(escape(request.POST['a21']))
        a22=float(escape(request.POST['a22']))

        A=numpy.array([[a11,a12],[a21,a22]])


        b=float(escape(request.POST['b']))
        a=float(escape(request.POST['a']))
        t0=float(escape(request.POST['t0']))
        hp=float(escape(request.POST['hp']))
        d=float(escape(request.POST['d']))

        Y0=X0
        N=len(A)
        alfa=numpy.max(numpy.abs(A))
        tl=[t0]
        Yl=[Y0]

        betal=[]

        hl=[]
        cl=[numpy.linalg.norm(Y0,'fro')]
        l1=[]
        l2=[]

        k=0;
        while tl[k]<t0+a:

              bet=numpy.max(b+abs(Yl[k]))
              betal.append(bet)
              h=numpy.sqrt(2*d/betal[k])/(alfa*N**1.25)
              hl.append(h)
              if sum(hl[:k])+hl[k]<=a:
                 if hl[k]>hp:
                    hl[k]=hl[k]
                    t=tl[k]+hl[k]
                    tl.append(t)
                    Y=numpy.add(Yl[k],numpy.dot(hl[k]*A,Yl[k]))
                    Yl.append(Y)
                    c=numpy.linalg.norm(Yl[k+1], 'fro')
                    cl.append(c)
                    l1.append(Yl[k][0][0])
                    l2.append(Yl[k][1][0])
                    tmp = {
                            'ite' : k,
                            'hi': "{0:.8f}".format(hl[k]),
                            'ti': "{0:.8f}".format(tl[k]),
                            'Xti': "{0:.8f}".format(cl[k]),
                            'x1ti': "{0:.8f}".format(l1[k]),
                            'x2ti': "{0:.8f}".format(l2[k])
                        }
                    result.append(tmp)
                    out.write("{:d}   {:.5f}  {:.5f}  {:.5f}  {:.5f}    {:.5f}\n".format(k,hl[k],tl[k],cl[k],l1[k],l2[k]))

              else:
                  if hl[k]>hp:
                     hl[k]=a-sum(hl[:k])

                     t=tl[k]+hl[k]
                     tl.append(t)
                     Y=numpy.add(Yl[k],numpy.dot(hl[k]*A,Yl[k]))
                     Yl.append(Y)
                     c=numpy.linalg.norm(Yl[k+1], 'fro')
                     cl.append(c)
                     l1.append(Yl[k][0][0])
                     l2.append(Yl[k][1][0])
                     tmp = {
                            'ite' : k,
                            'hi': "{0:.8f}".format(hl[k]),
                            'ti': "{0:.8f}".format(tl[k]),
                            'Xti':"{0:.8f}".format( cl[k]),

                            'x1ti': "{0:.8f}".format(l1[k]),
                            'x2ti': "{0:.8f}".format(l2[k])
                        }
                     result.append(tmp)
                     out.write("{:d}   {:.5f}  {:.5f}  {:.5f}  {:.5f}    {:.5f}\n".format(k,hl[k],tl[k],cl[k],l1[k],l2[k]))
              if hl[k]<hp:
                   hl[k]=0
                   break;

              k+=1

        out.close()
        book = xlwt.Workbook()
        ws = book.add_sheet('Euler Method') # Add a sheet
        excl = open("strategies/templates/textfiles/sisalgocl1.txt", 'r')
        data = excl.readlines() # read all lines at once
        for i in range(len(data)):
            row = data[i].split()  # This will return a line of string data, you may need to convert to other formats depending on your use cas
            for j in range(len(row)):
                ws.write(i, j, row[j])  # Write to cell i, j
        book.save("strategies/static/excelfiles/sisalgocl1.xls")
        excl.close()




     except:
          mycache = randint(1000, 10000)
     return render(request, 'graphics/sisalgoclf2.html', {'result':result,'calculations':calculations,'calculations_list':calculations_list,'result':result, 'mycache':mycache,'iletisims':iletisims, 'simulations':simulations , 'strategies': strategies,'simulations_list':simulations_list, 'strategies_list': strategies_list})

def sisalgoclf3(request):
     result=[]
     mycache = randint(1000, 10000)
     out=open("strategies/templates/textfiles/sisalgocl1.txt","w")
     out.write("i      hi        ti     ||X(ti)||   x1(ti)    x2(ti)\n")

     try:
        mycache = randint(1000, 10000)
        N=2
        result=[]

        x11=float(request.POST['x11'])
        x21=float(request.POST['x21'])

        X0=numpy.array([[x11],[x21]])

        a11=float(escape(request.POST['a11']))
        a12=float(escape(request.POST['a12']))
        a21=float(escape(request.POST['a21']))
        a22=float(escape(request.POST['a22']))

        A=numpy.array([[a11,a12],[a21,a22]])


        b=float(escape(request.POST['b']))
        a=float(escape(request.POST['a']))
        t0=float(escape(request.POST['t0']))
        hp=float(escape(request.POST['hp']))
        d=float(escape(request.POST['d']))

        Y0=X0
        N=len(A)
        alfa=numpy.max(numpy.abs(A))
        tl=[t0]
        Yl=[Y0]

        betal=[]

        hl=[]
        cl=[numpy.linalg.norm(Y0,'fro')]
        l1=[]
        l2=[]

        k=0;
        while tl[k]<t0+a:

              bet=numpy.max(b+abs(Yl[k]))
              betal.append(bet)
              h=numpy.sqrt(2*d/betal[k])/(alfa*N**1.25)
              hl.append(h)
              if sum(hl[:k])+hl[k]<=a:
                 if hl[k]>hp:
                    hl[k]=hl[k]
                    t=tl[k]+hl[k]
                    tl.append(t)
                    Y=numpy.add(Yl[k],numpy.dot(hl[k]*A,Yl[k]))
                    Yl.append(Y)
                    c=numpy.linalg.norm(Yl[k+1], 'fro')
                    cl.append(c)
                    l1.append(Yl[k][0][0])
                    l2.append(Yl[k][1][0])
                    tmp = {
                            'ite' : k,
                            'hi': hl[k],
                            'ti': tl[k],
                            'Xti': cl[k],
                            'x1ti': l1[k],
                            'x2ti': l2[k]
                        }
                    result.append(tmp)
                    out.write("{:d}   {:.5f}  {:.5f}  {:.5f}  {:.5f}    {:.5f}\n".format(k,hl[k],tl[k],cl[k],l1[k],l2[k]))

              else:
                  if hl[k]>hp:
                     hl[k]=a-sum(hl[:k])

                     t=tl[k]+hl[k]
                     tl.append(t)
                     Y=numpy.add(Yl[k],numpy.dot(hl[k]*A,Yl[k]))
                     Yl.append(Y)
                     c=numpy.linalg.norm(Yl[k+1], 'fro')
                     cl.append(c)
                     l1.append(Yl[k][0][0])
                     l2.append(Yl[k][1][0])
                     tmp = {
                            'ite' : k,
                            'hi': hl[k],
                            'ti': tl[k],
                            'Xti': cl[k],

                            'x1ti': l1[k],
                            'x2ti': l2[k]
                        }
                     result.append(tmp)
                     out.write("{:d}   {:.5f}  {:.5f}  {:.5f}  {:.5f}    {:.5f}\n".format(k,hl[k],tl[k],cl[k],l1[k],l2[k]))
              if hl[k]<hp:
                   hl[k]=0
                   break;

              k+=1

        out.close()
        book = xlwt.Workbook()
        ws = book.add_sheet('Euler Method') # Add a sheet
        excl = open("strategies/templates/textfiles/sisalgocl1.txt", 'r')
        data = excl.readlines() # read all lines at once
        for i in range(len(data)):
            row = data[i].split()  # This will return a line of string data, you may need to convert to other formats depending on your use cas
            for j in range(len(row)):
                ws.write(i, j, row[j])  # Write to cell i, j
        book.save("strategies/static/excelfiles/sisalgocl1.xls")
        excl.close()




     except:
          mycache = randint(1000, 10000)
     return render(request, 'graphics/sisalgoclf3.html', {'result':result,'calculations':calculations,'calculations_list':calculations_list,'result':result, 'mycache':mycache,'iletisims':iletisims, 'simulations':simulations , 'strategies': strategies,'simulations_list':simulations_list, 'strategies_list': strategies_list})





def picardcl(request):
     mycache = randint(1000, 10000)

     tl=[]
     xl=[]
     hl=[]
     Ml=[]
     al=[]
     try:
         mycache = randint(1000, 10000)
         t=Symbol('t')
         x=Symbol('x')

         expr=sympify(escape(request.POST['f']))

         v=lambdify((t,x),expr)

         def f(t1,x1):
             return v(t1,x1)


         hp=float(escape(request.POST['hp']))
         t0=float(escape(request.POST['t0']))
         tl.append(t0)
         x0=float(escape(request.POST['x0']))
         xl.append(x0)
         a=float(escape(request.POST['a']))
         b=float(escape(request.POST['b']))
         i=0;
         while tl[i]<t0+a:
             alf=numpy.linspace(tl[i]-a,tl[i]+a)
             bet=numpy.linspace(xl[i]-b,xl[i]+b)
             func=numpy.vectorize(f)
             M=max(abs(func(alf,bet)))
             Ml.append(M)
             h=min(a,b/Ml[i])
             hl.append(h)
             if sum(hl[:i])+hl[i]<=a:
                if hl[i]>hp:
                    hl[i]=hl[i]
                    t=tl[i]+hl[i]
                    x=xl[i]+hl[i]*f(tl[i],xl[i])
                    tl.append(t)
                    xl.append(x)

             else:
                 if hl[i]>hp:
                    hl[i]=a-sum(hl[:i])
                    t=tl[i]+hl[i]
                    x=xl[i]+hl[i]*f(tl[i],xl[i])
                    tl.append(t)
                    xl.append(x)

             if hl[i]<hp:
                hl[i]=0
                break;
             i+=1


         for k in range(len(hl)):
             al.append(k)
         pyplot.grid()
         pyplot.plot(tl,xl,'gs' ,linewidth=3)
         pyplot.legend([r'$x_{i}$'],fontsize=13)
         pyplot.xlabel(r'$t_{i}$',position=(1.01,-0.12),fontsize=13)
         pyplot.ylabel(r'$x_{i}$',position=(-0.1,1.01), fontsize=13, rotation='horizontal')
         pyplot.title('Numeric Solution')
         pyplot.savefig('strategies/static/graphics/images/picardcl.png')
         pyplot.close()

         pyplot.grid()
         pyplot.plot(al,hl,'bs' ,linewidth=3)
         pyplot.legend([r'$h_{i}$'], fontsize=13)
         pyplot.xlabel(r'$i$',position=(1.01,-0.12),fontsize=13)
         pyplot.ylabel(r'$h_{i}$',position=(-0.1,1.01), fontsize=13, rotation='horizontal')
         pyplot.title('Step Size')
         pyplot.savefig('strategies/static/graphics/images/picardhi.png')
         pyplot.close()





     except:
          mycache = randint(1000, 10000)
     return render(request, 'graphics/picardcl.html', {'calculations':calculations,'calculations_list':calculations_list,'iletisims':iletisims, 'mycache':mycache,'simulations':simulations , 'strategies': strategies,'simulations_list':simulations_list, 'strategies_list': strategies_list})

def picardclf(request):

     mycache = randint(1000, 10000)
     out=open("strategies/templates/textfiles/picardcl.txt","w")
     out.write("i        hi          ti          yi\n")
     tl=[]
     xl=[]
     hl=[]
     Ml=[]
     result=[]

     try:
         mycache = randint(1000, 10000)
         t=Symbol('t')
         x=Symbol('x')

         expr=sympify(escape(request.POST['f']))

         v=lambdify((t,x),expr)

         def f(t1,x1):
             return v(t1,x1)


         hp=float(escape(request.POST['hp']))
         t0=float(escape(request.POST['t0']))
         tl.append(t0)
         x0=float(escape(request.POST['x0']))
         xl.append(x0)
         a=float(escape(request.POST['a']))
         b=float(escape(request.POST['b']))
         i=0;
         while tl[i]<t0+a:
             alf=numpy.linspace(tl[i]-a,tl[i]+a)
             bet=numpy.linspace(xl[i]-b,xl[i]+b)
             func=numpy.vectorize(f)
             M=max(abs(func(alf,bet)))
             Ml.append(M)
             h=min(a,b/Ml[i])
             hl.append(h)
             if sum(hl[:i])+hl[i]<=a:
                if hl[i]>hp:
                    hl[i]=hl[i]
                    t=tl[i]+hl[i]
                    x=xl[i]+hl[i]*f(tl[i],xl[i])
                    tl.append(t)
                    xl.append(x)
                    tmp={'ite':i,
                          'hi':"{0:.8f}".format(hl[i]),
                          'ti':"{0:.8f}".format(tl[i]),
                          'xi':"{0:.8f}".format(xl[i])

                         }
                    result.append(tmp)
                    out.write("{:d}   {:.8f}    {:.8f}    {:.8f}\n".format(i,hl[i],tl[i],xl[i]))
             else:
                 if hl[i]>hp:
                    hl[i]=a-sum(hl[:i])
                    t=tl[i]+hl[i]
                    x=xl[i]+hl[i]*f(tl[i],xl[i])
                    tl.append(t)
                    xl.append(x)
                    tmp={'ite':i,
                          'hi':"{0:.8f}".format(hl[i]),
                          'ti':"{0:.8f}".format(tl[i]),
                          'xi':"{0:.8f}".format(xl[i])
                         }
                    result.append(tmp)
                    out.write("{:d}   {:.8f}    {:.8f}    {:.8f}\n".format(i,hl[i],tl[i],xl[i]))
             if hl[i]<hp:
                hl[i]=0
                break;
             i+=1




         out.close()
         book = xlwt.Workbook()
         ws = book.add_sheet('Euler Method') # Add a sheet
         excl = open("strategies/templates/textfiles/picardcl.txt", 'r')
         data = excl.readlines() # read all lines at once
         for i in range(len(data)):
             row = data[i].split()  # This will return a line of string data, you may need to convert to other formats depending on your use cas
             for j in range(len(row)):
                 ws.write(i, j, row[j])  # Write to cell i, j
         book.save("strategies/static/excelfiles/picardcl.xls")
         excl.close()


     except:
          mycache = randint(1000, 10000)
     return render(request, 'graphics/picardclf.html', {'result':result,'calculations':calculations,'calculations_list':calculations_list,'iletisims':iletisims, 'mycache':mycache,'simulations':simulations , 'strategies': strategies,'simulations_list':simulations_list, 'strategies_list': strategies_list})





def pihatacl(request):
     mycache = randint(1000, 10000)
     tl=[]
     xl=[]
     hl=[]
     Ml=[]
     TMl=[]
     bl=[]
     al=[]
     try:
         mycache = randint(1000, 10000)
         t=Symbol('t')
         x=Symbol('x')

         expr=sympify(escape(request.POST['f']))

         v=lambdify((t,x),expr)

         def f(t1,x1):
             return v(t1,x1)

         expr2=(Derivative(expr,x).doit())*expr+Derivative(expr,t).doit()

         df=lambdify((t,x),expr2)

         hp=float(request.POST['hp'])

         t0=float(request.POST['t0'])
         tl.append(t0)
         x0=float(request.POST['x0'])
         xl.append(x0)

         a=float(request.POST['a'])
         b=float(request.POST['b'])
         bl.append(b)

         alf=numpy.linspace(tl[0]-a,tl[0]+a)
         bet=numpy.linspace(xl[0]-b,xl[0]+b)
         func0=numpy.vectorize(f)
         M=max(abs(func0(alf,bet)))
         Ml.append(M)
         h0=min(a,b/float(Ml[0]))
         hl.append(h0)
         t=tl[0]+hl[0]
         tl.append(t)
         x=xl[0]+hl[0]*f(tl[0],xl[0])
         xl.append(x)

         i=1;
         while tl[i]<t0+a:
             alf1=numpy.linspace(tl[i]-a,tl[i]+a)
             bet1=numpy.linspace(xl[i-1]-bl[i-1],xl[i-1]+bl[i-1])
             func1=numpy.vectorize(df)
             TM=max(abs(func1(alf1,bet1)))
             TMl.append(TM)
             b1=min(bl[i-1],0.5*TMl[i-1]*hl[i-1]**2)
             bl.append(b1)
             alf2=numpy.linspace(tl[i]-a,tl[i]+a)
             bet2=numpy.linspace(xl[i]-bl[i],xl[i]+bl[i])
             M=max(abs(func0(alf2,bet2)))
             Ml.append(M)
             h=min(a,bl[i]/float(Ml[i]))
             hl.append(h)
             if sum(hl[:i])+hl[i]<=a:
                 if hl[i]>hp:
                    hl[i]=hl[i]
                    t=tl[i]+hl[i]
                    x=xl[i]+hl[i]*f(tl[i],xl[i])
                    tl.append(t)
                    xl.append(x)

             else:
                 if hl[i]>hp:
                    hl[i]=a-sum(hl[:i])
                    t=tl[i]+hl[i]
                    x=xl[i]+hl[i]*f(tl[i],xl[i])
                    tl.append(t)
                    xl.append(x)

             if hl[i]<hp:
                hl[i]=0
                break;
             i+=1



         for k in range(len(hl)):
             al.append(k)
         pyplot.grid()
         pyplot.plot(tl,xl,'gs')
         pyplot.legend([r'$x_{i}$'],fontsize=13)
         pyplot.xlabel(r'$t_{i}$',position=(1.01,-0.12),fontsize=13)
         pyplot.ylabel(r'$x_{i}$',position=(-0.1,1.01), fontsize=13, rotation='horizontal')
         pyplot.title('Numerical Solution')
         pyplot.savefig('strategies/static/graphics/images/pihatacl.png')
         pyplot.close()

         pyplot.grid()
         pyplot.plot(al,hl,'bs' ,linewidth=3)
         pyplot.legend([r'$h_{i}$'], fontsize=13)
         pyplot.xlabel(r'$i$',position=(1.01,-0.12),fontsize=13)
         pyplot.ylabel(r'$h_{i}$',position=(-0.1,1.01), fontsize=13, rotation='horizontal')
         pyplot.title('Step Size')
         pyplot.savefig('strategies/static/graphics/images/pihatahi.png')
         pyplot.close()






     except:
          mycache = randint(1000, 10000)
     return render(request, 'graphics/pihatacl.html', {'simulations':simulations ,'simulations_list':simulations_list ,'calculations':calculations,'calculations_list':calculations_list,'iletisims':iletisims, 'mycache': mycache, 'strategies': strategies,'calculations':calculations})



def pihataclf(request):
     results=[]
     mycache = randint(1000, 10000)
     out=open("strategies/templates/textfiles/pihataclf.txt","w")
     out.write("i        hi          ti          yi\n")
     tl=[]
     xl=[]
     hl=[]
     Ml=[]
     TMl=[]
     bl=[]

     try:
         mycache = randint(1000, 10000)
         t=Symbol('t')
         x=Symbol('x')

         expr=sympify(escape(request.POST['f']))

         v=lambdify((t,x),expr)

         def f(t1,x1):
             return v(t1,x1)

         expr2=(Derivative(expr,x).doit())*expr+Derivative(expr,t).doit()

         df=lambdify((t,x),expr2)

         hp=float(escape(request.POST['hp']))

         t0=float(escape(request.POST['t0']))
         tl.append(t0)
         x0=float(escape(request.POST['x0']))
         xl.append(x0)

         a=float(escape(request.POST['a']))
         b=float(escape(request.POST['b']))
         bl.append(b)

         alf=numpy.linspace(tl[0]-a,tl[0]+a)
         bet=numpy.linspace(xl[0]-b,xl[0]+b)
         func0=numpy.vectorize(f)
         M=max(abs(func0(alf,bet)))
         Ml.append(M)
         h0=min(a,b/float(Ml[0]))
         hl.append(h0)
         t=tl[0]+hl[0]
         tl.append(t)
         x=xl[0]+hl[0]*f(tl[0],xl[0])
         xl.append(x)
         out.write("{:d}   {:.6f}    {:.6f}    {:.6f}\n".format(0,hl[0],tl[0],xl[0]))
         tmp1={
                 'ite':0,
                  'hi':"{0:.6f}".format( hl[0]),
                  'ti':"{0:.6f}".format( tl[0]),
                 'xi':"{0:.6f}".format( xl[0]),

             }
         results.append(tmp1)
         i=1;
         while tl[i]<t0+a:
             alf1=numpy.linspace(tl[i]-a,tl[i]+a)
             bet1=numpy.linspace(xl[i-1]-bl[i-1],xl[i-1]+bl[i-1])
             func1=numpy.vectorize(df)
             TM=max(abs(func1(alf1,bet1)))
             TMl.append(TM)
             b1=min(bl[i-1],0.5*TMl[i-1]*hl[i-1]**2)
             bl.append(b1)
             alf2=numpy.linspace(tl[i]-a,tl[i]+a)
             bet2=numpy.linspace(xl[i]-bl[i],xl[i]+bl[i])
             M=max(abs(func0(alf2,bet2)))
             Ml.append(M)
             h=min(a,bl[i]/float(Ml[i]))
             hl.append(h)
             if sum(hl[:i])+hl[i]<=a:
                 if hl[i]>hp:
                    hl[i]=hl[i]
                    t=tl[i]+hl[i]
                    x=xl[i]+hl[i]*f(tl[i],xl[i])
                    tl.append(t)
                    xl.append(x)
                    xl.append(x)
                    tmp={'ite':i,
                          'hi':"{0:.6f}".format( hl[i]),
                          'ti':"{0:.6f}".format( tl[i]),
                          'xi':"{0:.6f}".format( xl[i]),

                         }
                    results.append(tmp)
                    out.write("{:d}   {:.6f}    {:6f}    {:.6f}\n".format(i,hl[i],tl[i],xl[i]))
             else:
                 if hl[i]>hp:
                    hl[i]=a-sum(hl[:i])
                    t=tl[i]+hl[i]
                    x=xl[i]+hl[i]*f(tl[i],xl[i])
                    tl.append(t)
                    xl.append(x)
                    tmp={'ite':i,
                          'hi':"{0:.6f}".format( hl[i]),
                          'ti':"{0:.6f}".format( tl[i]),
                          'xi':"{0:.6f}".format( xl[i]),

                         }
                    results.append(tmp)
                    out.write("{:d}   {:.6f}    {:6f}    {:.6f}\n".format(i,hl[i],tl[i],xl[i]))
             if hl[i]<hp:
                hl[i]=0
                break;
             i+=1


         out.close()
         book = xlwt.Workbook()
         ws = book.add_sheet('Euler Method') # Add a sheet
         excl = open("strategies/templates/textfiles/pihataclf.txt", 'r')
         data = excl.readlines() # read all lines at once
         for i in range(len(data)):
             row = data[i].split()  # This will return a line of string data, you may need to convert to other formats depending on your use cas
             for j in range(len(row)):
                 ws.write(i, j, row[j])  # Write to cell i, j
         book.save("strategies/static/excelfiles/pihataclf.xls")
         excl.close()


     except:
          mycache = randint(1000, 10000)
     return render(request, 'graphics/pihataclf.html', {'results':results, 'simulations':simulations ,'simulations_list':simulations_list ,'calculations':calculations,'calculations_list':calculations_list,'iletisims':iletisims, 'mycache': mycache, 'strategies': strategies,'calculations':calculations})




def nonsisalgocl1(request):
     mycache = randint(1000, 10000)

     try:
        mycache = randint(1000, 10000)


        x11=float(request.POST['x11'])
        x21=float(request.POST['x21'])

        X0=numpy.array([[x11],[x21]])

        a11=float(escape(request.POST['a11']))
        a12=float(escape(request.POST['a12']))
        a21=float(escape(request.POST['a21']))
        a22=float(escape(request.POST['a22']))

        A=numpy.array([[a11,a12],[a21,a22]])

        N=len(A)

        b=float(escape(request.POST['b']))
        a=float(escape(request.POST['a']))
        t0=float(escape(request.POST['t0']))
        hp=float(escape(request.POST['hp']))
        d=float(escape(request.POST['d']))

        x=sympify(escape(request.POST['dv1']))
        y=sympify(escape(request.POST['dv2']))

        t=Symbol('t')
        x=Symbol('x')
        y=Symbol('y')

        symbls=[t,x,y]
        X=numpy.array([[x],[y]])

        fi0=sympify(escape(request.POST['fi0']))
        fi1=sympify(escape(request.POST['fi1']))

        gfi=lambdify((t,x,y),Matrix([[fi0],[fi1]]))

        def fi(t,x,y):
            return gfi(t,x,y)
        m=[]
        q=[]
        n=[]



        for i in range(len(gfi(t,x,y))):
            for j in symbls:
                l=Derivative(gfi(t,x,y)[i][0],j).doit()
                m.append(l)

        fii=numpy.array(m).reshape((N,N+1))

        eqs=numpy.add(numpy.dot(A,X),fi(t,x,y))

        for i in range(len(eqs)):
            q.append(eqs[i][0])

        q.append(1)
        qq=numpy.array(q).reshape((N+1,1))

        fit=numpy.dot(fii,qq)

        for i in range(len(fit)):
            n.append(fit[i][0])

        r=lambdify((t,x,y),Matrix(n))

        def dfi(t,x,y):
            return r(t,x,y)


        Y0=X0
        alf=numpy.max(numpy.abs(A))
        tl=[t0]
        Yl=[Y0]

        betal=[]
        etal=[]
        gamal=[]

        hl=[]
        cl=[numpy.linalg.norm(Y0,'fro')]
        l1=[]
        l2=[]
        ye=[]
        al=[]
        k=0;
        while tl[k]<t0+a:
              tetaa=numpy.linspace(t0-a,t0+a)
              betaa=numpy.max(b+abs(Yl[k]))
              betal.append(betaa)
              gamaa=numpy.max(abs(fi(numpy.max(tetaa),betal[k],betal[k])))
              gamal.append(gamaa)
              etaa=numpy.max(abs(dfi(numpy.max(tetaa),betal[k],betal[k])))
              etal.append(etaa)
              h=numpy.sqrt(2*d/((N**2)*betal[k]*(alf**2)+N*alf*gamal[k]+etal[k]))/(N**0.25)
              hl.append(h)
              if sum(hl[:k])+hl[k]<=a:
                  if hl[k]>hp:
                      hl[k]=hl[k]
                      ti=tl[k]+hl[k]
                      tl.append(ti)
                      Y=numpy.add(numpy.add(Yl[k],numpy.dot(hl[k]*A,Yl[k])),hl[k]*fi(tl[k],Yl[k][0][0],Yl[k][1][0]))
                      Yl.append(Y)
                      c=numpy.linalg.norm(Yl[k+1], 'fro')
                      cl.append(c)
                      l1.append(Yl[k][0][0])
                      l2.append(Yl[k][1][0])

              else:
                  if hl[k]>hp:
                      hl[k]=a-sum(hl[:k])
                      ti=tl[k]+hl[k]
                      tl.append(ti)
                      Y=numpy.add(numpy.add(Yl[k],numpy.dot(hl[k]*A,Yl[k])),hl[k]*fi(tl[k],Yl[k][0][0],Yl[k][1][0]))
                      Yl.append(Y)
                      c=numpy.linalg.norm(Yl[k+1], 'fro')
                      cl.append(c)
                      l1.append(Yl[k][0][0])
                      l2.append(Yl[k][1][0])
              if hl[k]<hp:
                  hl[k]=0
                  break;
              k+=1


        for k in range(len(hl)):
            al.append(k)



        for i in range(len(tl)-1):
            ye.append(tl[i])
        pyplot.figure(1)
        pyplot.grid()
        pyplot.plot(tl,cl,'gs', linewidth=3)
        pyplot.legend([r'$||X_{i}||$'],fontsize=13)
        pyplot.ylabel(r'$||X_{i}||$',position=(-0.1,1.01), fontsize=13, rotation='horizontal')
        pyplot.xlabel(r'$t_{i}$',position=(1.01,-0.12),fontsize=13)
        pyplot.title('Norm of Numeric Solution')
        pyplot.savefig('strategies/static/graphics/images/nonsis2x2norm.png')
        pyplot.close()

        pyplot.figure(2)
        pyplot.grid()
        pyplot.plot(al,hl,'bs' ,linewidth=3)
        pyplot.legend([r'$h_{i}$'],fontsize=13)
        pyplot.xlabel(r'$i$',position=(1.01,-0.12),fontsize=13)
        pyplot.ylabel(r'$h_{i}$',position=(-0.1,1.01), fontsize=13, rotation='horizontal')
        pyplot.title('Step Size')
        pyplot.savefig('strategies/static/graphics/images/nonsis2x2stepsize.png')
        pyplot.close()


        pyplot.figure(3)
        pyplot.grid()
        pyplot.plot(ye,l1,'cs' ,linewidth=3)
        pyplot.legend([r'$x_{i}$'],fontsize=13)
        pyplot.xlabel(r'$t_{i}$',position=(1.01,-0.12),fontsize=13)
        pyplot.ylabel(r'$x_{i}$',position=(-0.1,1.01), fontsize=13, rotation='horizontal')
        pyplot.title('First Component')
        pyplot.savefig('strategies/static/graphics/images/nonsis2x2x1.png')
        pyplot.close()

        pyplot.figure(4)
        pyplot.grid()
        pyplot.plot(ye,l2,'ms' ,linewidth=3)
        pyplot.legend([r'$y_{i}$'],fontsize=13)
        pyplot.xlabel(r'$t_{i}$',position=(1.01,-0.12),fontsize=13)
        pyplot.ylabel(r'$y_{i}$',position=(-0.1,1.01), fontsize=13, rotation='horizontal')
        pyplot.title('Second Component')
        pyplot.savefig('strategies/static/graphics/images/nonsis2x2x2.png')
        pyplot.close()

        pyplot.figure(5)
        pyplot.grid()
        pyplot.plot(l1,l2,'m-' ,linewidth=3)
        pyplot.xlabel(r'$y_{1}$',position=(1.01,-0.12),fontsize=13)
        pyplot.ylabel(r'$y_{2}$',position=(-0.1,1.01), fontsize=13, rotation='horizontal')
        pyplot.title('First-Second Component')
        pyplot.savefig('strategies/static/graphics/images/nonsis2x2x1x2.png')
        pyplot.close()





     except:
          mycache = randint(1000, 10000)
     return render(request, 'graphics/nonsisalgocl1.html', {'calculations':calculations,'calculations_list':calculations_list, 'mycache':mycache,'iletisims':iletisims, 'simulations':simulations , 'strategies': strategies,'simulations_list':simulations_list, 'strategies_list': strategies_list})


def nonsisalgocl2(request):
     mycache = randint(1000, 10000)

     try:
        mycache = randint(1000, 10000)

        x11=float(request.POST['x11'])
        x21=float(request.POST['x21'])
        x31=float(request.POST['x31'])

        X0=numpy.array([[x11],[x21],[x31]])

        a11=float(escape(request.POST['a11']))
        a12=float(escape(request.POST['a12']))
        a13=float(escape(request.POST['a13']))

        a21=float(escape(request.POST['a21']))
        a22=float(escape(request.POST['a22']))
        a23=float(escape(request.POST['a23']))

        a31=float(escape(request.POST['a31']))
        a32=float(escape(request.POST['a32']))
        a33=float(escape(request.POST['a33']))



        A=numpy.array([[a11,a12,a13],[a21,a22,a23],[a31,a32,a33]])

        N=len(A)

        b=float(escape(request.POST['b']))
        a=float(escape(request.POST['a']))
        t0=float(escape(request.POST['t0']))
        hp=float(escape(request.POST['hp']))
        d=float(escape(request.POST['d']))


        x=sympify(escape(request.POST['dv1']))
        y=sympify(escape(request.POST['dv2']))
        z=sympify(escape(request.POST['dv3']))

        t=Symbol('t')
        x=Symbol('x')
        y=Symbol('y')
        z=Symbol('z')

        symbls=[t,x,y,z]
        X=numpy.array([[x],[y],[z]])

        fi0=sympify(escape(request.POST['fi0']))
        fi1=sympify(escape(request.POST['fi1']))
        fi2=sympify(escape(request.POST['fi2']))

        gfi=lambdify((t,x,y,z),Matrix([[fi0],[fi1],[fi2]]))

        def fi(t,x,y,z):
            return gfi(t,x,y,z)
        m=[]
        q=[]
        n=[]



        for i in range(len(gfi(t,x,y,z))):
            for j in symbls:
                l=Derivative(gfi(t,x,y,z)[i][0],j).doit()
                m.append(l)

        fii=numpy.array(m).reshape((N,N+1))

        eqs=numpy.add(numpy.dot(A,X),fi(t,x,y,z))

        for i in range(len(eqs)):
            q.append(eqs[i][0])

        q.append(1)
        qq=numpy.array(q).reshape((N+1,1))

        fit=numpy.dot(fii,qq)

        for i in range(len(fit)):
            n.append(fit[i][0])

        r=lambdify((t,x,y,z),Matrix(n))

        def dfi(t,x,y,z):
            return r(t,x,y,z)


        Y0=X0
        alf=numpy.max(numpy.abs(A))
        tl=[t0]
        Yl=[Y0]

        betal=[]
        etal=[]
        gamal=[]

        hl=[]
        cl=[numpy.linalg.norm(Y0,'fro')]
        l1=[]
        l2=[]
        l3=[]
        ye=[]
        al=[]
        k=0;
        while tl[k]<t0+a:
              tetaa=numpy.linspace(t0-a,t0+a)
              betaa=numpy.max(b+abs(Yl[k]))
              betal.append(betaa)
              gamaa=numpy.max(abs(fi(numpy.max(tetaa),betal[k],betal[k],betal[k])))
              gamal.append(gamaa)
              etaa=numpy.max(abs(dfi(numpy.max(tetaa),betal[k],betal[k],betal[k])))
              etal.append(etaa)
              h=numpy.sqrt(2*d/((N**2)*betal[k]*(alf**2)+N*alf*gamal[k]+etal[k]))/(N**0.25)
              hl.append(h)
              if sum(hl[:k])+hl[k]<=a:
                  if hl[k]>hp:
                      hl[k]=hl[k]
                      ti=tl[k]+hl[k]
                      tl.append(ti)
                      Y=numpy.add(numpy.add(Yl[k],numpy.dot(hl[k]*A,Yl[k])),hl[k]*fi(tl[k],Yl[k][0][0],Yl[k][1][0],Yl[k][2][0]))
                      Yl.append(Y)
                      c=numpy.linalg.norm(Yl[k+1], 'fro')
                      cl.append(c)
                      l1.append(Yl[k][0][0])
                      l2.append(Yl[k][1][0])
                      l3.append(Yl[k][2][0])

              else:
                  if hl[k]>hp:
                      hl[k]=a-sum(hl[:k])
                      ti=tl[k]+hl[k]
                      tl.append(ti)
                      Y=numpy.add(numpy.add(Yl[k],numpy.dot(hl[k]*A,Yl[k])),hl[k]*fi(tl[k],Yl[k][0][0],Yl[k][1][0],Yl[k][2][0]))
                      Yl.append(Y)
                      c=numpy.linalg.norm(Yl[k+1], 'fro')
                      cl.append(c)
                      l1.append(Yl[k][0][0])
                      l2.append(Yl[k][1][0])
                      l3.append(Yl[k][2][0])
              if hl[k]<hp:
                  hl[k]=0
                  break;
              k+=1


        for k in range(len(hl)):
            al.append(k)



        for i in range(len(tl)-1):
            ye.append(tl[i])

        pyplot.figure(1)
        pyplot.grid()
        pyplot.plot(tl,cl,'gs', linewidth=3)
        pyplot.legend([r'$||X_{i}||$'],fontsize=13)
        pyplot.ylabel(r'$||X_{i}||$',position=(-0.1,1.01), fontsize=13, rotation='horizontal')
        pyplot.xlabel(r'$t_{i}$',position=(1.01,-0.12),fontsize=13)
        pyplot.title('Norm of Numerical Solution')
        pyplot.savefig('strategies/static/graphics/images/nonsisalgocl1.png')
        pyplot.close()

        pyplot.figure(2)
        pyplot.grid()
        pyplot.plot(al,hl,'bs' ,linewidth=3)
        pyplot.legend([r'$h_{i}$'],fontsize=13)
        pyplot.xlabel(r'$i$',position=(1.01,-0.12),fontsize=13)
        pyplot.ylabel(r'$h_{i}$',position=(-0.1,1.01), fontsize=13, rotation='horizontal')
        pyplot.title('Step Size')
        pyplot.savefig('strategies/static/graphics/images/nonsisalgohi.png')
        pyplot.close()


        pyplot.figure(3)
        pyplot.grid()
        pyplot.plot(ye,l1,'cs' ,linewidth=3)
        pyplot.legend([r'$x_{i}$'],fontsize=13)
        pyplot.xlabel(r'$t_{i}$',position=(1.01,-0.12),fontsize=13)
        pyplot.ylabel(r'$x_{i}$',position=(-0.1,1.01), fontsize=13, rotation='horizontal')
        pyplot.title('First Component')
        pyplot.savefig('strategies/static/graphics/images/nonsisx1.png')
        pyplot.close()

        pyplot.figure(4)
        pyplot.grid()
        pyplot.plot(ye,l2,'rs' ,linewidth=3)
        pyplot.legend([r'$y_{i}$'],fontsize=13)
        pyplot.xlabel(r'$t_{i}$',position=(1.01,-0.12),fontsize=13)
        pyplot.ylabel(r'$y_{i}$',position=(-0.1,1.01), fontsize=13, rotation='horizontal')
        pyplot.title('Second Component')
        pyplot.savefig('strategies/static/graphics/images/nonsisx2.png')
        pyplot.close()

        pyplot.figure(5)
        pyplot.grid()
        pyplot.plot(ye,l3,'ms' ,linewidth=3)
        pyplot.legend([r'$z_{i}$'],fontsize=13)
        pyplot.xlabel(r'$t_{i}$',position=(1.01,-0.12),fontsize=13)
        pyplot.ylabel(r'$z_{i}$',position=(-0.1,1.01), fontsize=13, rotation='horizontal')
        pyplot.title('Third Component')
        pyplot.savefig('strategies/static/graphics/images/nonsisx3.png')
        pyplot.close()

        mpl.rcParams['legend.fontsize'] = 10
        fig = plt.figure(6)
        ax = fig.add_subplot(111, projection='3d')
        ax.plot(l1, l2, l3, label='Numerical Solution', color='r')
        ax.legend()
        ax.set_xlabel(r'$X_{i}$',fontsize=13)

        ax.set_ylabel(r'$Y_{i}$',fontsize=13)

        ax.set_zlabel(r'$Z_{i}$',fontsize=13)




        pyplot.savefig('strategies/static/graphics/images/deneme3d.png')

        fig = plt.figure(7)
        ax = p3.Axes3D(fig)





     except:
          mycache = randint(1000, 10000)
     return render(request, 'graphics/nonsisalgocl2.html', {'calculations':calculations,'calculations_list':calculations_list, 'mycache':mycache,'iletisims':iletisims, 'simulations':simulations , 'strategies': strategies,'simulations_list':simulations_list, 'strategies_list': strategies_list})



def nonsisalgocl3(request):
     mycache = randint(1000, 10000)

     try:
        mycache = randint(1000, 10000)

        x11=float(request.POST['x11'])
        x21=float(request.POST['x21'])
        x31=float(request.POST['x31'])
        x41=float(request.POST['x41'])

        X0=numpy.array([[x11],[x21],[x31],[x41]])

        a11=float(escape(request.POST['a11']))
        a12=float(escape(request.POST['a12']))
        a13=float(escape(request.POST['a13']))
        a14=float(escape(request.POST['a14']))

        a21=float(escape(request.POST['a21']))
        a22=float(escape(request.POST['a22']))
        a23=float(escape(request.POST['a23']))
        a24=float(escape(request.POST['a24']))

        a31=float(escape(request.POST['a31']))
        a32=float(escape(request.POST['a32']))
        a33=float(escape(request.POST['a33']))
        a34=float(escape(request.POST['a34']))

        a41=float(escape(request.POST['a41']))
        a42=float(escape(request.POST['a42']))
        a43=float(escape(request.POST['a43']))
        a44=float(escape(request.POST['a44']))

        A=numpy.array([[a11,a12,a13,a14],[a21,a22,a23,a24],[a31,a32,a33,a34],[a41,a42,a43,a44]])

        N=len(A)

        b=float(escape(request.POST['b']))
        a=float(escape(request.POST['a']))
        t0=float(escape(request.POST['t0']))
        hp=float(escape(request.POST['hp']))
        d=float(escape(request.POST['d']))


        x=sympify(escape(request.POST['dv1']))
        y=sympify(escape(request.POST['dv2']))
        z=sympify(escape(request.POST['dv3']))
        w=sympify(escape(request.POST['dv4']))

        t=Symbol('t')
        x=Symbol('x')
        y=Symbol('y')
        z=Symbol('z')
        w=Symbol('w')

        symbls=[t,x,y,z,w]
        X=numpy.array([[x],[y],[z],[w]])

        fi0=sympify(escape(request.POST['fi0']))
        fi1=sympify(escape(request.POST['fi1']))
        fi2=sympify(escape(request.POST['fi2']))
        fi3=sympify(escape(request.POST['fi3']))

        gfi=lambdify((t,x,y,z,w),Matrix([[fi0],[fi1],[fi2],[fi3]]))

        def fi(t,x,y,z,w):
            return gfi(t,x,y,z,w)
        m=[]
        q=[]
        n=[]



        for i in range(len(gfi(t,x,y,z,w))):
            for j in symbls:
                l=Derivative(gfi(t,x,y,z,w)[i][0],j).doit()
                m.append(l)

        fii=numpy.array(m).reshape((N,N+1))

        eqs=numpy.add(numpy.dot(A,X),fi(t,x,y,z,w))

        for i in range(len(eqs)):
            q.append(eqs[i][0])

        q.append(1)
        qq=numpy.array(q).reshape((N+1,1))

        fit=numpy.dot(fii,qq)

        for i in range(len(fit)):
            n.append(fit[i][0])

        r=lambdify((t,x,y,z,w),Matrix(n))

        def dfi(t,x,y,z,w):
            return r(t,x,y,z,w)


        Y0=X0
        alf=numpy.max(numpy.abs(A))
        tl=[t0]
        Yl=[Y0]

        betal=[]
        etal=[]
        gamal=[]

        hl=[]
        cl=[numpy.linalg.norm(Y0,'fro')]
        l1=[]
        l2=[]
        l3=[]
        l4=[]
        ye=[]
        al=[]
        k=0;
        while tl[k]<t0+a:
              tetaa=numpy.linspace(t0-a,t0+a)
              betaa=numpy.max(b+abs(Yl[k]))
              betal.append(betaa)
              gamaa=numpy.max(abs(fi(numpy.max(tetaa),betal[k],betal[k],betal[k],betal[k])))
              gamal.append(gamaa)
              etaa=numpy.max(abs(dfi(numpy.max(tetaa),betal[k],betal[k],betal[k],betal[k])))
              etal.append(etaa)
              h=numpy.sqrt(2*d/((N**2)*betal[k]*(alf**2)+N*alf*gamal[k]+etal[k]))/(N**0.25)
              hl.append(h)
              if sum(hl[:k])+hl[k]<=a:
                  if hl[k]>hp:
                      hl[k]=hl[k]
                      ti=tl[k]+hl[k]
                      tl.append(ti)
                      Y=numpy.add(numpy.add(Yl[k],numpy.dot(hl[k]*A,Yl[k])),hl[k]*fi(tl[k],Yl[k][0][0],Yl[k][1][0],Yl[k][2][0],Yl[k][3][0]))
                      Yl.append(Y)
                      c=numpy.linalg.norm(Yl[k+1], 'fro')
                      cl.append(c)
                      l1.append(Yl[k][0][0])
                      l2.append(Yl[k][1][0])
                      l3.append(Yl[k][2][0])
                      l4.append(Yl[k][3][0])

              else:
                  if hl[k]>hp:
                      hl[k]=a-sum(hl[:k])
                      ti=tl[k]+hl[k]
                      tl.append(ti)
                      Y=numpy.add(numpy.add(Yl[k],numpy.dot(hl[k]*A,Yl[k])),hl[k]*fi(tl[k],Yl[k][0][0],Yl[k][1][0],Yl[k][2][0],Yl[k][3][0]))
                      Yl.append(Y)
                      c=numpy.linalg.norm(Yl[k+1], 'fro')
                      cl.append(c)
                      l1.append(Yl[k][0][0])
                      l2.append(Yl[k][1][0])
                      l3.append(Yl[k][2][0])
                      l4.append(Yl[k][3][0])
              if hl[k]<hp:
                  hl[k]=0
                  break;
              k+=1


        for k in range(len(hl)):
            al.append(k)



        for i in range(len(tl)-1):
            ye.append(tl[i])

        pyplot.figure(1)
        pyplot.grid()
        pyplot.plot(tl,cl,'gs', linewidth=3)
        pyplot.legend([r'$||X_{i}||$'], fontsize=13)
        pyplot.ylabel(r'$||X_{i}||$',position=(-0.1,1.01), fontsize=13, rotation='horizontal')
        pyplot.xlabel(r'$t_{i}$',position=(1.01,-0.12),fontsize=13)
        pyplot.title('Norm of Numeric Solution')
        pyplot.savefig('strategies/static/graphics/images/nonsisalgocl1.png')
        pyplot.close()

        pyplot.figure(2)
        pyplot.grid()
        pyplot.plot(al,hl,'bs' ,linewidth=3)
        pyplot.legend([r'$h_{i}$'], fontsize=13)
        pyplot.xlabel(r'$i$',position=(1.01,-0.12),fontsize=13)
        pyplot.ylabel(r'$h_{i}$',position=(-0.1,1.01), fontsize=13, rotation='horizontal')
        pyplot.title('Step Size')
        pyplot.savefig('strategies/static/graphics/images/nonsisalgohi.png')
        pyplot.close()


        pyplot.figure(3)
        pyplot.grid()
        pyplot.plot(ye,l1,'cs' ,linewidth=3)
        pyplot.legend([r'$x_{i}$'], fontsize=13)
        pyplot.xlabel(r'$t_{i}i$',position=(1.01,-0.12),fontsize=13)
        pyplot.ylabel(r'$x_{i}$',position=(-0.1,1.01), fontsize=13, rotation='horizontal')
        pyplot.title('First Component')
        pyplot.savefig('strategies/static/graphics/images/nonsisx1.png')
        pyplot.close()

        pyplot.figure(4)
        pyplot.grid()
        pyplot.plot(ye,l2,'ms' ,linewidth=3)
        pyplot.legend([r'$y_{i}$'], fontsize=13)
        pyplot.xlabel(r'$t_{i}$',position=(1.01,-0.12),fontsize=13)
        pyplot.ylabel(r'$y_{i}$',position=(-0.1,1.01), fontsize=13, rotation='horizontal')
        pyplot.title('Second Component')
        pyplot.savefig('strategies/static/graphics/images/nonsisx2.png')
        pyplot.close()

        pyplot.figure(5)
        pyplot.grid()
        pyplot.plot(ye,l3,'ks' ,linewidth=3)
        pyplot.legend([r'$z_{i}$'], fontsize=13)
        pyplot.xlabel(r'$t_{i}$',position=(1.01,-0.12),fontsize=13)
        pyplot.ylabel(r'$z_{i}$',position=(-0.1,1.01), fontsize=13, rotation='horizontal')
        pyplot.title('Third Component')
        pyplot.savefig('strategies/static/graphics/images/nonsisx3.png')
        pyplot.close()

        pyplot.figure(6)
        pyplot.grid()
        pyplot.plot(ye,l4,'ys' ,linewidth=3)
        pyplot.legend([r'$w_{i}$'], fontsize=13)
        pyplot.xlabel(r'$t_{i}$',position=(1.01,-0.12),fontsize=13)
        pyplot.ylabel(r'$w_{i}$',position=(-0.1,1.01), fontsize=13, rotation='horizontal')
        pyplot.title('Fourth Component')
        pyplot.savefig('strategies/static/graphics/images/nonsisx4.png')
        pyplot.close()





     except:
          mycache = randint(1000, 10000)
     return render(request, 'graphics/nonsisalgocl3.html', {'calculations':calculations,'calculations_list':calculations_list, 'mycache':mycache,'iletisims':iletisims, 'simulations':simulations , 'strategies': strategies,'simulations_list':simulations_list, 'strategies_list': strategies_list})








def nonsisalgoclf1(request):
     result=[]
     mycache = randint(1000, 10000)
     out=open("strategies/templates/textfiles/nonsisalgocl1.txt","w")
     out.write("i      hi        ti     ||X(ti)||    x1(ti)    x2(ti)\n")
     try:
        mycache = randint(1000, 10000)

        x11=float(request.POST['x11'])
        x21=float(request.POST['x21'])

        X0=numpy.array([[x11],[x21]])

        a11=float(escape(request.POST['a11']))
        a12=float(escape(request.POST['a12']))
        a21=float(escape(request.POST['a21']))
        a22=float(escape(request.POST['a22']))

        A=numpy.array([[a11,a12],[a21,a22]])

        N=len(A)

        b=float(escape(request.POST['b']))
        a=float(escape(request.POST['a']))
        t0=float(escape(request.POST['t0']))
        hp=float(escape(request.POST['hp']))
        d=float(escape(request.POST['d']))

        x=sympify(escape(request.POST['dv1']))
        y=sympify(escape(request.POST['dv2']))

        t=Symbol('t')
        x=Symbol('x')
        y=Symbol('y')

        symbls=[t,x,y]
        X=numpy.array([[x],[y]])

        fi0=sympify(escape(request.POST['fi0']))
        fi1=sympify(escape(request.POST['fi1']))

        fi00=lambdify((t,x,y),fi0)


        gfi=lambdify((t,x,y),Matrix([[fi00(t,x,y)],[fi1]]))

        def fi(t,x,y):
            return gfi(t,x,y)
        m=[]
        q=[]
        n=[]



        for i in range(len(gfi(t,x,y))):
            for j in symbls:
                l=Derivative(gfi(t,x,y)[i][0],j).doit()
                m.append(l)

        fii=numpy.array(m).reshape((N,N+1))

        eqs=numpy.add(numpy.dot(A,X),fi(t,x,y))

        for i in range(len(eqs)):
            q.append(eqs[i][0])

        q.append(1)
        qq=numpy.array(q).reshape((N+1,1))

        fit=numpy.dot(fii,qq)

        for i in range(len(fit)):
            n.append(fit[i][0])

        r=lambdify((t,x,y),Matrix(n))

        def dfi(t,x,y):
            return r(t,x,y)


        Y0=X0
        alf=numpy.max(numpy.abs(A))
        tl=[t0]
        Yl=[Y0]

        betal=[]
        etal=[]
        gamal=[]

        hl=[]
        cl=[numpy.linalg.norm(Y0,'fro')]
        l1=[]
        l2=[]
        ye=[]
        al=[]
        k=0;
        while tl[k]<t0+a:
              tetaa=numpy.linspace(t0-a,t0+a)
              betaa=numpy.max(b+abs(Yl[k]))
              betal.append(betaa)
              gamaa=numpy.max(abs(fi(numpy.max(tetaa),betal[k],betal[k])))
              gamal.append(gamaa)
              etaa=numpy.max(abs(dfi(numpy.max(tetaa),betal[k],betal[k])))
              etal.append(etaa)
              h=numpy.sqrt(2*d/((N**2)*betal[k]*(alf**2)+N*alf*gamal[k]+etal[k]))/(N**0.25)
              hl.append(h)
              if sum(hl[:k])+hl[k]<=a:
                  if hl[k]>hp:
                      hl[k]=hl[k]
                      ti=tl[k]+hl[k]
                      tl.append(ti)
                      Y=numpy.add(numpy.add(Yl[k],numpy.dot(hl[k]*A,Yl[k])),hl[k]*fi(tl[k],Yl[k][0][0],Yl[k][1][0]))
                      Yl.append(Y)
                      c=numpy.linalg.norm(Yl[k+1], 'fro')
                      cl.append(c)
                      l1.append(Yl[k][0][0])
                      l2.append(Yl[k][1][0])
                      tmp = {
                            'ite' : k,
                            'hi': hl[k],
                            'ti': tl[k],
                            'Xti': cl[k],
                            'x1ti': l1[k],
                            'x2ti': l2[k]
                        }
                      result.append(tmp)
                      out.write("{:d}   {:.9f}  {:.9f}  {:.9f}  {:.9f}    {:.9f}\n".format(k,hl[k],tl[k],cl[k],l1[k],l2[k]))

              else:
                  if hl[k]>hp:
                      hl[k]=a-sum(hl[:k])
                      ti=tl[k]+hl[k]
                      tl.append(ti)
                      Y=numpy.add(numpy.add(Yl[k],numpy.dot(hl[k]*A,Yl[k])),hl[k]*fi(tl[k],Yl[k][0][0],Yl[k][1][0]))
                      Yl.append(Y)
                      c=numpy.linalg.norm(Yl[k+1], 'fro')
                      cl.append(c)
                      l1.append(Yl[k][0][0])
                      l2.append(Yl[k][1][0])
                      tmp = {
                            'ite' : k,
                            'hi': hl[k],
                            'ti': tl[k],
                            'Xti': cl[k],
                            'x1ti': l1[k],
                            'x2ti': l2[k]
                        }
                      result.append(tmp)
                      out.write("{:d}   {:.9f}  {:.9f}  {:.9f}  {:.9f}    {:.9f}\n".format(k,hl[k],tl[k],cl[k],l1[k],l2[k]))
              if hl[k]<hp:
                   hl[k]=0
                   break;


              k+=1

        out.close()

        book = xlwt.Workbook()
        ws = book.add_sheet('Euler Method') # Add a sheet
        excl = open("strategies/templates/textfiles/nonsisalgocl1.txt", 'r')
        data = excl.readlines() # read all lines at once
        for i in range(len(data)):
            row = data[i].split()  # This will return a line of string data, you may need to convert to other formats depending on your use cas
            for j in range(len(row)):
                ws.write(i, j, row[j])  # Write to cell i, j
        book.save("strategies/static/excelfiles/nonsisalgocl1.xls")
        excl.close()








     except:
          mycache = randint(1000, 10000)
     return render(request, 'graphics/nonsisalgoclf1.html', {'result':result,'calculations':calculations,'calculations_list':calculations_list, 'mycache':mycache,'iletisims':iletisims, 'simulations':simulations , 'strategies': strategies,'simulations_list':simulations_list, 'strategies_list': strategies_list})


def nonsisalgoclf2(request):
     result=[]
     mycache = randint(1000, 10000)
     out=open("strategies/templates/textfiles/nonsisalgoclf2.txt","w")
     out.write("i      hi        ti     ||X(ti)||    x1(ti)    x2(ti)    x3(ti)\n")
     mycache = randint(1000, 10000)
     try:
        mycache = randint(1000, 10000)

        x11=float(request.POST['x11'])
        x21=float(request.POST['x21'])
        x31=float(request.POST['x31'])

        X0=numpy.array([[x11],[x21],[x31]])

        a11=float(escape(request.POST['a11']))
        a12=float(escape(request.POST['a12']))
        a13=float(escape(request.POST['a13']))

        a21=float(escape(request.POST['a21']))
        a22=float(escape(request.POST['a22']))
        a23=float(escape(request.POST['a23']))

        a31=float(escape(request.POST['a31']))
        a32=float(escape(request.POST['a32']))
        a33=float(escape(request.POST['a33']))

        A=numpy.array([[a11,a12,a13],[a21,a22,a23],[a31,a32,a33]])

        N=len(A)

        b=float(escape(request.POST['b']))
        a=float(escape(request.POST['a']))
        t0=float(escape(request.POST['t0']))
        hp=float(escape(request.POST['hp']))
        d=float(escape(request.POST['d']))


        x=sympify(escape(request.POST['dv1']))
        y=sympify(escape(request.POST['dv2']))
        z=sympify(escape(request.POST['dv3']))

        t=Symbol('t')
        x=Symbol('x')
        y=Symbol('y')
        z=Symbol('z')

        symbls=[t,x,y,z]
        X=numpy.array([[x],[y],[z]])

        fi0=sympify(escape(request.POST['fi0']))
        fi1=sympify(escape(request.POST['fi1']))
        fi2=sympify(escape(request.POST['fi2']))

        gfi=lambdify((t,x,y,z),Matrix([[fi0],[fi1],[fi2]]))

        def fi(t,x,y,z):
            return gfi(t,x,y,z)
        m=[]
        q=[]
        n=[]



        for i in range(len(gfi(t,x,y,z))):
            for j in symbls:
                l=Derivative(gfi(t,x,y,z)[i][0],j).doit()
                m.append(l)

        fii=numpy.array(m).reshape((N,N+1))

        eqs=numpy.add(numpy.dot(A,X),fi(t,x,y,z))

        for i in range(len(eqs)):
            q.append(eqs[i][0])

        q.append(1)
        qq=numpy.array(q).reshape((N+1,1))

        fit=numpy.dot(fii,qq)

        for i in range(len(fit)):
            n.append(fit[i][0])

        r=lambdify((t,x,y,z),Matrix(n))

        def dfi(t,x,y,z):
            return r(t,x,y,z)


        Y0=X0
        alf=numpy.max(numpy.abs(A))
        tl=[t0]
        Yl=[Y0]

        betal=[]
        etal=[]
        gamal=[]

        hl=[]
        cl=[numpy.linalg.norm(Y0,'fro')]
        l1=[]
        l2=[]
        l3=[]
        ye=[]
        al=[]
        k=0;
        while tl[k]<t0+a:
              tetaa=numpy.linspace(t0-a,t0+a)
              betaa=numpy.max(b+abs(Yl[k]))
              betal.append(betaa)
              gamaa=numpy.max(abs(fi(numpy.max(tetaa),betal[k],betal[k],betal[k])))
              gamal.append(gamaa)
              etaa=numpy.max(abs(dfi(numpy.max(tetaa),betal[k],betal[k],betal[k])))
              etal.append(etaa)
              h=numpy.sqrt(2*d/((N**2)*betal[k]*(alf**2)+N*alf*gamal[k]+etal[k]))/(N**0.25)
              hl.append(h)
              if sum(hl[:k])+hl[k]<=a:
                  if hl[k]>hp:
                      hl[k]=hl[k]
                      ti=tl[k]+hl[k]
                      tl.append(ti)
                      Y=numpy.add(numpy.add(Yl[k],numpy.dot(hl[k]*A,Yl[k])),hl[k]*fi(tl[k],Yl[k][0][0],Yl[k][1][0],Yl[k][2][0]))
                      Yl.append(Y)
                      c=numpy.linalg.norm(Yl[k+1], 'fro')
                      cl.append(c)
                      l1.append(Yl[k][0][0])
                      l2.append(Yl[k][1][0])
                      l3.append(Yl[k][2][0])
                      tmp = {
                           'ite' : k,
                            'hi': "{0:.8f}".format(hl[k]),
                            'ti': "{0:.8f}".format(tl[k]),
                            'Xti': "{0:.8f}".format(cl[k]),
                            'x1ti': "{0:.8f}".format(l1[k]),
                            'x2ti': "{0:.8f}".format(l2[k]),
                            'x3ti': "{0:.8f}".format(l3[k])
                        }
                      result.append(tmp)
                      out.write("{:d}   {:.8f}  {:.8f}  {:.8f}    {:.8f}    {:.8f}  {:.8f}\n".format(k,hl[k],tl[k],cl[k],l1[k],l2[k],l3[k]))

              else:
                  if hl[k]>hp:
                      hl[k]=a-sum(hl[:k])
                      ti=tl[k]+hl[k]
                      tl.append(ti)
                      Y=numpy.add(numpy.add(Yl[k],numpy.dot(hl[k]*A,Yl[k])),hl[k]*fi(tl[k],Yl[k][0][0],Yl[k][1][0],Yl[k][2][0]))
                      Yl.append(Y)
                      c=numpy.linalg.norm(Yl[k+1], 'fro')
                      cl.append(c)
                      l1.append(Yl[k][0][0])
                      l2.append(Yl[k][1][0])
                      l3.append(Yl[k][2][0])
                      tmp = {
                            'ite' : k,
                            'hi': "{0:.8f}".format(hl[k]),
                            'ti': "{0:.8f}".format(tl[k]),
                            'Xti': "{0:.8f}".format(cl[k]),
                            'x1ti': "{0:.8f}".format(l1[k]),
                            'x2ti': "{0:.8f}".format(l2[k]),
                            'x3ti': "{0:.8f}".format(l3[k])
                        }
                      result.append(tmp)
                      out.write("{:d}   {:.8f}  {:.8f}  {:.8f}    {:.8f}    {:.8f}  {:.8f}\n".format(k,hl[k],tl[k],cl[k],l1[k],l2[k],l3[k]))
              if hl[k]<hp:
                  hl[k]=0
                  break;
              k+=1

        out.close()

        book = xlwt.Workbook()
        ws = book.add_sheet('Euler Method') # Add a sheet
        excl = open("strategies/templates/textfiles/nonsisalgoclf2.txt", 'r')
        data = excl.readlines() # read all lines at once
        for i in range(len(data)):
            row = data[i].split()  # This will return a line of string data, you may need to convert to other formats depending on your use cas
            for j in range(len(row)):
                ws.write(i, j, row[j])  # Write to cell i, j
        book.save("strategies/static/excelfiles/nonsisalgoclf2.xls")
        excl.close()








     except:
          mycache = randint(1000, 10000)
     return render(request, 'graphics/nonsisalgoclf2.html', {'result':result,'calculations':calculations,'calculations_list':calculations_list, 'mycache':mycache,'iletisims':iletisims, 'simulations':simulations , 'strategies': strategies,'simulations_list':simulations_list, 'strategies_list': strategies_list})

def nonsisalgoclf3(request):
     result=[]
     mycache = randint(1000, 10000)
     out=open("strategies/templates/textfiles/nonsisalgocl1.txt","w")
     out.write("i      hi        ti     ||X(ti)||    x1(ti)    x2(ti)\n")
     try:
        mycache = randint(1000, 10000)

        x11=float(request.POST['x11'])
        x21=float(request.POST['x21'])

        X0=numpy.array([[x11],[x21]])

        a11=float(escape(request.POST['a11']))
        a12=float(escape(request.POST['a12']))
        a21=float(escape(request.POST['a21']))
        a22=float(escape(request.POST['a22']))

        A=numpy.array([[a11,a12],[a21,a22]])

        N=len(A)

        b=float(escape(request.POST['b']))
        a=float(escape(request.POST['a']))
        t0=float(escape(request.POST['t0']))
        hp=float(escape(request.POST['hp']))
        d=float(escape(request.POST['d']))

        x=sympify(escape(request.POST['dv1']))
        y=sympify(escape(request.POST['dv2']))

        t=Symbol('t')
        x=Symbol('x')
        y=Symbol('y')

        symbls=[t,x,y]
        X=numpy.array([[x],[y]])

        fi0=sympify(escape(request.POST['fi0']))
        fi1=sympify(escape(request.POST['fi1']))

        fi00=lambdify((t,x,y),fi0)


        gfi=lambdify((t,x,y),Matrix([[fi00(t,x,y)],[fi1]]))

        def fi(t,x,y):
            return gfi(t,x,y)
        m=[]
        q=[]
        n=[]



        for i in range(len(gfi(t,x,y))):
            for j in symbls:
                l=Derivative(gfi(t,x,y)[i][0],j).doit()
                m.append(l)

        fii=numpy.array(m).reshape((N,N+1))

        eqs=numpy.add(numpy.dot(A,X),fi(t,x,y))

        for i in range(len(eqs)):
            q.append(eqs[i][0])

        q.append(1)
        qq=numpy.array(q).reshape((N+1,1))

        fit=numpy.dot(fii,qq)

        for i in range(len(fit)):
            n.append(fit[i][0])

        r=lambdify((t,x,y),Matrix(n))

        def dfi(t,x,y):
            return r(t,x,y)


        Y0=X0
        alf=numpy.max(numpy.abs(A))
        tl=[t0]
        Yl=[Y0]

        betal=[]
        etal=[]
        gamal=[]

        hl=[]
        cl=[numpy.linalg.norm(Y0,'fro')]
        l1=[]
        l2=[]
        ye=[]
        al=[]
        k=0;
        while tl[k]<t0+a:
              tetaa=numpy.linspace(t0-a,t0+a)
              betaa=numpy.max(b+abs(Yl[k]))
              betal.append(betaa)
              gamaa=numpy.max(abs(fi(numpy.max(tetaa),betal[k],betal[k])))
              gamal.append(gamaa)
              etaa=numpy.max(abs(dfi(numpy.max(tetaa),betal[k],betal[k])))
              etal.append(etaa)
              h=numpy.sqrt(2*d/((N**2)*betal[k]*(alf**2)+N*alf*gamal[k]+etal[k]))/(N**0.25)
              hl.append(h)
              if sum(hl[:k])+hl[k]<=a:
                  if hl[k]>hp:
                      hl[k]=hl[k]
                      ti=tl[k]+hl[k]
                      tl.append(ti)
                      Y=numpy.add(numpy.add(Yl[k],numpy.dot(hl[k]*A,Yl[k])),hl[k]*fi(tl[k],Yl[k][0][0],Yl[k][1][0]))
                      Yl.append(Y)
                      c=numpy.linalg.norm(Yl[k+1], 'fro')
                      cl.append(c)
                      l1.append(Yl[k][0][0])
                      l2.append(Yl[k][1][0])
                      tmp = {
                            'ite' : k,
                            'hi': hl[k],
                            'ti': tl[k],
                            'Xti': cl[k],
                            'x1ti': l1[k],
                            'x2ti': l2[k]
                        }
                      result.append(tmp)
                      out.write("{:d}   {:.9f}  {:.9f}  {:.9f}  {:.9f}    {:.9f}\n".format(k,hl[k],tl[k],cl[k],l1[k],l2[k]))

              else:
                  if hl[k]>hp:
                      hl[k]=a-sum(hl[:k])
                      ti=tl[k]+hl[k]
                      tl.append(ti)
                      Y=numpy.add(numpy.add(Yl[k],numpy.dot(hl[k]*A,Yl[k])),hl[k]*fi(tl[k],Yl[k][0][0],Yl[k][1][0]))
                      Yl.append(Y)
                      c=numpy.linalg.norm(Yl[k+1], 'fro')
                      cl.append(c)
                      l1.append(Yl[k][0][0])
                      l2.append(Yl[k][1][0])
                      tmp = {
                            'ite' : k,
                            'hi': "{0:.5f}".format(hl[k]),
                            'ti': "{0:.5f}".format(tl[k]),
                            'Xti': "{0:.5f}".format(cl[k]),
                            'x1ti': "{0:.5f}".format(l1[k]),
                            'x2ti': "{0:.5f}".format(l2[k])
                        }
                      result.append(tmp)
                      out.write("{:d}   {:.9f}  {:.9f}  {:.9f}  {:.9f}    {:.9f}\n".format(k,hl[k],tl[k],cl[k],l1[k],l2[k]))
              if hl[k]<hp:
                   hl[k]=0
                   break;


              k+=1

        out.close()

        book = xlwt.Workbook()
        ws = book.add_sheet('Euler Method') # Add a sheet
        excl = open("strategies/templates/textfiles/nonsisalgocl1.txt", 'r')
        data = excl.readlines() # read all lines at once
        for i in range(len(data)):
            row = data[i].split()  # This will return a line of string data, you may need to convert to other formats depending on your use cas
            for j in range(len(row)):
                ws.write(i, j, row[j])  # Write to cell i, j
        book.save("strategies/static/excelfiles/nonsisalgocl1.xls")
        excl.close()








     except:
          mycache = randint(1000, 10000)
     return render(request, 'graphics/nonsisalgoclf3.html', {'result':result,'calculations':calculations,'calculations_list':calculations_list, 'mycache':mycache,'iletisims':iletisims, 'simulations':simulations , 'strategies': strategies,'simulations_list':simulations_list, 'strategies_list': strategies_list})



