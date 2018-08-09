import re
import sys
import os
from time import sleep
import regex #see https://stackoverflow.com/questions/26385984/recursive-pattern-in-regex 
import pygame
from pygame.locals import *
import numpy
import math
from functions import *
from tkinter import filedialog
from tkinter import *
 

def start_up_screen():
	class broken:
		def __init__(self,name):
			self.name=name
			self.b=0
		def break_now(self):
			self.b=1
	class file_name: 
		def __init__(self,name):
			self.name=name
			self.filename="Upload File Above"
		def update(self):
			self.filename=filedialog.askopenfilename(initialdir = "~/Desktop/",title = "Select file",filetypes = (("tex files","*.tex"),("all files","*.*")))
	filename=file_name("use_file")
	broke=broken("use_broken")
	root = Tk()
	root.geometry("500x500")
	btn = Button(root, text="Insert File", command=lambda: filename.update())
	btn.pack()
	T = Text(root,state='disabled', height=2, width=30)#https://www.python-course.eu/tkinter_text_widget.php
	T.pack()
	T2 = Text(root, height=2, width=35)#https://www.python-course.eu/tkinter_text_widget.php
	T2.pack()
	T2.insert(END,"Please insert start point box below")
	T3 = Text(root, height=2, width=40)#https://www.python-course.eu/tkinter_text_widget.php
	T3.pack()
	T3.insert(END,"")
	break_btn=Button(root, text="Submit", command=lambda: broke.break_now())
	break_btn.pack()
	while True:
		T.configure(state='normal')
		T.delete('1.0', END)
		T.insert(END,filename.filename)
		T.configure(state='disabled')
		start_point=T3.get("1.0",'end-1c')
		if broke.b==1:
			break
		sleep(0.25)
		root.update()
	root.destroy()
	return start_point, filename.filename
start_point,file_name=start_up_screen()

f=open(file_name,"r")
content_temp=f.readlines()
f.close()

content=""
new_commands=[]
for x in content_temp:
	content=content+x.split("%")[0]
f=open("./beamer_template.tex","r")
tex_content=f.read()
f.close()

#varibles used later
voice_type=0

content=commands_in_text(content)
#Go to start point
#if start_point!="":#if it is just start from begining.
#	content=r"\begin{document}"+"".join(content.split(start_point)[1:])
#else:
content=r"\begin{document}"+"".join(content.split(r"\begin{document}")[1:])



content,equations_from_seperation=remove_eqs(content)#These equations are added in show and say loops 
#findandreplace
content,figures_from_seperation,incude_graphic_from_seperation=remove_figs(content)#I am yet to add these back in.
dire=[[r"""\section""","Section00EndSection00Start"],[r"""\subsection""","SubSection01EndSubSection01Start"],[r"""\subsubsection""","SubSubSection02EndSubSubSection02Start"],[r"""begin{document}""","BeginDocument{Pre Section}"],[r"""\end{document}""","EndDocument"],[r"""\n\n""",r"""ParaEndParaStart"""]]#,[r""".""","SentanceEndSentanceStart"]]
for x in dire:
	content=content.replace(x[0],x[1])
content=re.sub(r"\.[^0-9]","SentanceEndSentanceStart",content,0)#as don't want to split e.g. numbers 1.2

#Here I will work down levels progressivly
sentences=[]
sections_temp=re.findall("(BeginDocument|Section00Start){(.*?)}(.*?)(Section00End|EndDocument)",content,re.DOTALL)
sections=[[x[1],"STARTSTRING"+x[2]+"ENDSTRING"] for x in sections_temp]#[title,content]

for sec in sections:#subsections
	temp=re.findall("(STARTSTRING|SubSection01Start)(.*?)(Section00End|EndDocument|SubSection01End|ENDSTRING)",sec[1],re.DOTALL)
	sec[1]=["STARTSTRING"+x[1]+"ENDSTRING" for x in temp]
	for subsec in sec[1]: #paragraphs
		temp=re.findall("(STARTSTRING|ParaStart)(.*?)(Section00End|EndDocument|SubSection01End|ParaEnd|ENDSTRING)",subsec,re.DOTALL)
		subsec=["STARTSTRING"+x[1]+"ENDSTRING" for x in temp]
		for para in subsec: #Sentances
			temp=re.findall("(STARTSTRING|SentanceStart)(.*?)(Section00End|EndDocument|SubSection01End|ParaEnd|SentanceEnd|ENDSTRING)",para,re.DOTALL)
			para=[x[1] for x in temp]
			sentences.append([sec[0],[x[1] for x in temp]])


#.........Display Code
pygame.init()
#pygame_screen = pygame.display.set_mode((1280,700), 0, 32)
pygame.display.set_caption('paper2lecture')
icon=pygame.image.load("./icon/icon.png")
pygame.display.set_icon(icon)
pygame_screen=pygame.display.set_mode((1280,700),HWSURFACE|DOUBLEBUF|RESIZABLE)

#...............................................
#...............................................
#...............................................
#...............................................
#...............................................
#...............................................
#Start text			

def main_loop(start_point):
	id_start_sec=0
	broken=0
	while id_start_sec<len(sentences):
		id_start_sent=0
		while id_start_sent<len(sentences[id_start_sec][1]):
			if start_point in sentences[id_start_sec][1][id_start_sent]:
				broken=1
				print("broken")
				break
			id_start_sent=id_start_sent+1
		if broken==1:
			break
		id_start_sec=id_start_sec+1

	sentences_start=sentences[id_start_sec:]
	sentences_start[0]=[sentences_start[0][0],sentences_start[0][1][id_start_sent:]]

	for y in sentences_start:
		to_show=""
		sent_with_equ=[]
		for m in y[1]: #show
			show=add_eqs(m,equations_from_seperation)#adding equations back in
			equterms=[[r"""$""","EqInline"],[r"""begin{equation}""","EqDisp"],[r"""end{equation}""","EqDisp"],[r"""begin{multiline}""","EqDisp"],[r"""end{multiline}""","EqDisp"],[r"""\[""","EqDisp"],[r"""\]""","EqDisp"]]#used later.
			no_eqs=len([ x[0] for x in equterms if x[0] in show])
			show=show_editor(show)
			if no_eqs!=0 or include_in_ppt(show):
				sent_with_equ.append(show)

		try:
			pages=[["~",sent_with_equ[0],sent_with_equ[1]]]+[[sent_with_equ[n],sent_with_equ[n+1],sent_with_equ[n+2]] for n in range(0,len(sent_with_equ)-3)]+[[sent_with_equ[len(sent_with_equ)-2],sent_with_equ[len(sent_with_equ)-1]]]
		except IndexError:
			pages=[sent_with_equ+["~"]]
		for pag in pages:
			to_show=to_show+r"""\begin{frame}\begin{itemize} """
			item_no=0
			for x in pag:
				if item_no==1:
					to_show=to_show+r""" \item """+str(x)
				else:
					to_show=to_show+r""" \item {\color{gray} """+str(x)+r"""}"""

				item_no=item_no+1
			to_show=to_show+r""" \end{itemize}\end{frame}"""
		tex_content_temp=tex_content.replace("<main_text>",to_show)
		tex_content_temp=packages(tex_content_temp,content)
		f=open("temp_beamer.tex","w")
		f.write(tex_content_temp)
		f.close()
		os.system("pdflatex temp_beamer.tex")
		os.system("pdftk A=temp_beamer.pdf cat A1 output temp_pg.pdf")
		img_display=display_update(pygame_screen)	
		cleaner()
		n=0
		#...............................................
		#...............................................
		for m in y[1]:#say
			say=add_eqs(m,equations_from_seperation)
			say,len_equations=say_editor(say)
			if len_equations>0 or include_in_ppt(say):
				os.system("pdftk A=temp_beamer.pdf cat A"+str(n+1)+" output temp_pg.pdf")
				img_display=display_update(pygame_screen)	
				n=n+1
			print(say)

			#if voice_type==1:
			#	os.system('spd-say -y english -t male1 -r -60 -p 25 -w  -m none "'+say+'" ')#the -w here is vital
				#spd-say -y english -t male1 -r 70 -p 25 -w  -m none "hello"

			#else:
			words=say.split(" ")
			n=0
			while n < len(words):
				if voice_type==0:
					os.system('spd-say -o pico-generic -w -m none "'+words[n]+'" ')#the -w here is vital
					sleep(numpy.abs(numpy.random.normal(0.5,0.1)))
					n=n+1
				if voice_type==1:
					say_here=" ".join(words[n:])
					os.system('spd-say -y english -t male1 -r -60 -p 25 -w  -m none "'+say_here+'" ')#the -w here is vital
					n=len(words)
				event_output=pygame_events(img_display,pygame_screen)
					
						

main_loop(start_point)
