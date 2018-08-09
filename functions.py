import re
import sys
import os
from time import sleep
import regex #see https://stackoverflow.com/questions/26385984/recursive-pattern-in-regex 
import pygame
from pygame.locals import *
import numpy
import math
def commands_in_text(content):
	with_args=regex.findall(r"newcommand{([^\[\{]*)}\[([1-9])\]({((?>[^{}]+|(?3))*)})",content,regex.DOTALL)
	without_args=regex.findall(r"newcommand{([^\[\{]*)}({((?>[^{}]+|(?2))*)})",content,regex.DOTALL)+regex.findall(r"\\def(.*?)({((?>[^{}]+|(?2))*)})",content,regex.DOTALL)#the ([^\[]*) is to stop it capturing once with arguments.
	for y in reversed(with_args):
		arguments=""
		for n in range(0,int(y[1])):
			arguments=arguments+"({((?>[^{}]+|(?"+str(2*n+1)+"))*)})"
		instances=regex.findall(regex.escape(y[0])+arguments,content,regex.DOTALL)
		for ins in instances:
			to_include=y[3]
			for n in range(0,int(len(ins)/2)):
				to_include=to_include.replace("#"+str(n+1),ins[2*n+1])
			argm_inst=""
			for n in  range(0,int(len(ins)/2)):
				argm_inst="{"+ins[2*n+1]+"}"
			content=content.replace(y[0]+argm_inst,to_include)
	for y in reversed(without_args):
		instances=regex.findall(regex.escape(y[0])+'([^a-zA-Z])',content,regex.DOTALL) 
		for ins in instances:
			content=content.replace(y[0]+ins[0], y[2]+ins[0])
	return content
def remove_eqs(text_in):#used in multiple places so be careful with edits
	equations=regex.findall(r"(\$|\\\[|\\begin{\equation}|\\begin\*{\equation}|\\begin{multiline}|\\begin\*{multiline}|\\begin{\eqnarray}|\\begin\*{\eqnarray})(((.*?)({((?>[^{}]+|(?5))*)})*(.*?))*)(\$|\\\]|\\end{\equation}|\\end\*{\equation}|\\end{multiline}|\\end\*{multiline}|\\end{\eqnarray}|\\end\*{\eqnarray})",text_in,regex.DOTALL)
	text_temp=text_in
	for n in range(0,len(equations)):
		text_temp=text_temp.replace(equations[n][0]+equations[n][1]+equations[n][7],"EQATION-PLACEHOLDER"+str(n)+"-id")
	text_out=text_temp
	return list([text_out,equations])
def add_eqs(text_in,equations):#used in multiple places so be careful with edits
	text_temp=text_in
	for n in range(0,len(equations)):
		text_temp=text_temp.replace("EQATION-PLACEHOLDER"+str(n)+"-id",equations[n][0]+equations[n][1]+equations[n][7])
	text_out=text_temp
	return text_out
def remove_figs(text_in):#really need to have includegrpahic here aswell.
	text_temp=text_in
	figures=re.findall(r"(\\begin{figure})(.*?)(\\end{figure})",text_in,re.DOTALL)
	for n in range(0,len(figures)):
		text_temp=text_temp.replace(figures[n][0]+figures[n][1]+figures[n][2],"FIGURE-PLACEHOLDER"+str(n)+"-id")
	# e.g. \includegraphics[scale=0.34]{hidden_decay.pdf}
	include_graphic=re.findall(r"\\includegraphics\[(.*?)\]{(.*?)}",text_in,re.DOTALL)
	for n in range(0,len(include_graphic)):
		text_temp=text_temp.replace(r"\includegraphics["+include_graphic[n][0]+"]{"+include_graphic[n][1]+"}","INCLUDEIMAGE-PLACEHOLDER"+str(n)+"-id")
	text_out=text_temp
	return list([text_out,figures,include_graphic])
def add_figs(text_in,figures,include_graphic):
	text_temp=text_in
	for n in range(0,len(figures)):
		text_temp=text_temp.replace("FIGURE-PLACEHOLDER"+str(n)+"-id",figures[n][0]+figures[n][1]+figures[n][2])
	for n in range(0,len(include_graphic)):
		text_temp=text_temp.replace("INCLUDEIMAGE-PLACEHOLDER"+str(n)+"-id",r"\includegraphics["+include_graphic[n][0]+"]{"+include_graphic[n][1]+"}")
	text_out=text_temp
	return text_out
def remove_unbracketed_commands(text_in):
	text_temp=text_in
	#https://regex101.com/r/SZW5OB/1
	commands_to_remove=[["vskip","[0-9.]+"]]
	for y in commands_to_remove:
		text_temp=re.sub(r"\\"+re.escape(y[0])+r"\s+"+y[1],"",text_temp)
	text_out=text_temp
	return text_out
def remove_bracketed_commands_lose_content(text_in):
	text_temp=text_in
	#https://regex101.com/r/SZW5OB/1
	commands_to_remove=[["begin","[a-zA-Z0-9.]+"],["end","[a-zA-Z0-9.]+"],["vspace","[a-zA-Z0-9.]+"]]
	for y in commands_to_remove:
		text_temp=re.sub(r"\\"+re.escape(y[0])+r"{+"+y[1]+r"}","",text_temp)
	text_out=text_temp
	return text_out
def maths_to_say(in_maths):
	output_0=in_maths
	greek=[[r"""\alpha"""," alpha "],[r"""\beta"""," beta "],[r"""\gamma"""," gamma "],[r"""\Gamma"""," gamma "],[r"""\delta"""," delta "],[r"""\Delta"""," delta "],[r"""\epsilon"""," epsilon "],[r"""\varepsilon"""," varepsilon "],[r"""\zeta"""," zeta "],[r"""\eta"""," eta "],[r"""\theta"""," theta "],[r"""\vartheta"""," theta "],[r"""\Theta"""," theta "],[r"""\iota"""," iota "],[r"""\kappa"""," kappa "],[r"""\lambda"""," lambda "],[r"""\Lambda"""," lambda "],[r"""\mu"""," mu "],[r"""\nu"""," nu "],[r"""\xi"""," xi "],[r"""\Xi"""," xi "],[r"""\pi"""," pi "],[r"""\Pi"""," pi "],[r"""\rho"""," rho "],[r"""\varrho"""," rho "],[r"""\sigma"""," sigma "],[r"""\Sigma"""," sigma "],[r"""\tau"""," tau "],[r"""\upsilon"""," upsilon "],[r"""\Upsilon"""," upsilon "],[r"""\phi"""," phi "],[r"""\varphi"""," phi "],[r"""\Phi"""," phi "],[r"""\chi"""," chi "],[r"""\psi"""," psi "],[r"""\Psi"""," psi "],[r"""\omega"""," omega "],[r"""\Omega"""," omgea "]]
	others=[[r"""\ell""", " l "]]
	for x in greek+others:
		output_0=output_0.replace(x[0],x[1])
	output_0=re.sub(r"\\(mathcal|mathscr|mathrm){(|\s+)([a-zA-Z])(|\s+)}",r" \2 ",output_0) #\mathcal{O} \mathscr{O} \mathrm{O}
	output_0=re.sub(r"{\\(mathcal|mathscr|mathrm)(|\s+)([a-zA-Z])}",r" \3 ",output_0) #{\mathcal O} etc
	output_0=re.sub(r"\\(cal|scr|rm|vec)(|\s+)([a-zA-Z])",r" \3 ",output_0) #{\mathcal O} etc including {\vec}
	output_0=re.sub(r"-",r" minus ",output_0) #{\mathcal O} etc including {\vec}
	
	
	#after here if no changes made will set to no-speak.
	temp=output_0
	output=output_0
	output=re.sub(r"\A([a-zA-Z]+|[0-9]+|\s)+$",r" \1 ",output) #any string of words and numbers only
	output=re.sub(r"\A([a-zA-Z]+|[0-9]+|\s)+=([a-zA-Z]+|[0-9]+|\s)+$",r"\1 equals \2",output) #a=1
	output=re.sub(r"\A([a-zA-Z]+|[0-9]+)_([0-9]+|[a-zA-Z]+|)$",r"\1  \2",output) #a_2
	output=re.sub(r"\A([a-zA-Z]+|[0-9]+)\^([0-9]+|[a-zA-Z]+|)$",r"\1 \2",output) #a^2
	output=re.sub(r"\A([a-zA-Z]+|[0-9]+|\s)+=-([a-zA-Z]+|[0-9]+|\s)+$",r"\1 equals minus \2",output) #a=-1
	output=re.sub(r"\A([a-zA-Z]+|[0-9]+|\s)+/([a-zA-Z]+|[0-9]+|\s)+$",r"\1 over \2",output) #a/b
	#...
	temp=re.findall(r"\A(|\s)+([0-9]+).([0-9]+)(|\s)+$",output) #103.23
	for x in temp:
		temp_st=''
		for y in x[2]:
			temp_st=temp_st+' '+y
		output=x[1]+" point "+temp_st
	#...
	if output==output_0:
		output=""
	return output

def include_in_ppt(show):
	include_or_not=0
	terms_to_include=["analogy","consider","definition", "define", "suppose","take to" ]
	for y in terms_to_include:
		if y in show:
			include_or_not=1
	if include_or_not==0:
		return False
	else:
		return True
def packages(tex_content_temp,content):
	packages_with_extra=re.findall(r"usepackage\[(.*?)\]{(.*?)}",content,re.DOTALL)
	packages_without_extra_temp=re.findall(r"usepackage{(.*?)}",content,re.DOTALL)
	packages_without_extra=[]
	for y in packages_without_extra_temp:#removes any cases where more then one package put in same 'usepackage'
		if "," in y:
			packages_without_extra=packages_without_extra+y.split(",")
		else:
			packages_without_extra.append(y)
	print("Packages You Don't Have: ")
	list_of_packages=""
	for y in packages_without_extra+packages_with_extra:
		f=open("package_test_file.tex","w")
		if isinstance(y, str):
			f.write(r"\documentclass{article}\usepackage{"+y+"}"+r"\begin{document}\end{document}")
		else:
			f.write(r"\documentclass{article}\usepackage["+y[0]+"]{"+y[1]+"}"+r"\begin{document}\end{document}")
		f.close()
		output=os.popen("pdflatex -interaction=nonstopmode package_test_file.tex").read()
		if "Fatal error occurred, no output PDF file produced" in output:
			print(y)
		else:
			if isinstance(y, str):
				list_of_packages=list_of_packages+r" \usepackage{"+y+"}"
			else:
				list_of_packages=list_of_packages+r" \usepackage{"+y[0]+"}"
	return tex_content_temp.replace("<packages>",list_of_packages)

def show_editor(show):
	output=show
	cite_lable_subsection_ref=re.findall("(cite|lable|subsection|ref){(.*?)}",output,re.DOTALL)#removes e.g. cite lable etc
	
	for x in cite_lable_subsection_ref:
			output=output.replace("\\"+x[0]+"{"+x[1]+"}","")
	#............Creating string without maths in
	no_maths=output
	no_maths,equations=remove_eqs(no_maths)
	#do stuff to no_maths here i.e. what needs to be done to normal text but not to maths.
	no_maths=remove_unbracketed_commands(no_maths)
	no_maths=remove_bracketed_commands_lose_content(no_maths)
	no_maths=re.sub(r"\\([a-zA-Z]+)",r"",no_maths)#Here we get rid of formating. It is this that needs to be edited if want to keep it. I have removed it here to eliminate any stray brackets which lead to a fatal error.
	remove_from_no_maths=["{","}"]
	for y in remove_from_no_maths:
		no_maths=no_maths.replace(y,"")
	#end of do stuff to no_maths
	output=add_eqs(no_maths,equations)
	#..........end of no maths
	return output
def cleaner():#clears up files left behind.
	tex_endings=[".aux",".out",".log",".nav",".snm",".toc"]
	file_starters=["temp_beamer","package_test_file"]
	for f in file_starters:
		for e in tex_endings:
			os.system("rm "+f+e)
def display_update(pygame_screen):
	os.system("convert temp_pg.pdf beamer.jpg")
	img = pygame.image.load("beamer.jpg")
	#pygame_screen.blit(img, (0, 0)) #Replace (0, 0) with desired coordinates
	pygame_screen.blit(pygame.transform.scale(img,(1280,700)),(0,0))
	pygame.display.flip()
	return img
	
def say_editor(text_in):
	text_temp=text_in
	text_temp=remove_unbracketed_commands(text_temp)
	#equations
	equterms=[[r"""$""","EqInline"],[r"""\begin{equation}""","EqDisp"],[r"""\end{equation}""","EqDisp"],[r"""\begin{multiline}""","EqDisp"],[r"""\end{multiline}""","EqDisp"],[r"""\begin{eqnarray}""","EqDisp"],[r"""\end{eqnarray}""","EqDisp"],[r"""[\\""","EqDisp"],[r"""\]""","EqDisp"]]#used later.
	for x in equterms:
			text_temp=text_temp.replace(x[0],x[1])
	equations=re.findall("(EqInline|EqDisp)(.*?)(EqInline|EqDisp)",text_temp,re.DOTALL)
	for x in equations:
			text_temp=text_temp.replace(x[0]+x[1]+x[2],maths_to_say(x[1]))
	#end of equations
	#removes e.g. cite lable etc
	annoying_terms=re.findall("(cite|lable|begin|end|subsection|ref|vspace)(|\*){(.*?)}",text_temp,re.DOTALL)
	for x in annoying_terms:
			text_temp=text_temp.replace(x[0]+x[1]+"{"+x[2]+"}","")
	text_temp=re.sub(r'\\(.*?){(.*?)}',r' \2 ',text_temp)
	#removing other commands
	text_temp=re.sub(r"\\[a-zA-Z]*","",text_temp)
	#removes all non-alphanumeric (if every want to do maths this will bad)
	text_temp=re.sub('[^A-Za-z0-9,.;:]+', ' ', text_temp)
	text_out=text_temp
	return list([text_out,len(equations)])
def help_menu(pygame_screen):
	width, height = pygame.display.get_surface().get_size() 
	WHITE = (255, 255, 255)
	BLACK = (  0,   0,   0)
	size= [width*0.25, height*0.25, width*0.5, height*0.5] #left top width height
	font_size=25
	rectwhite=pygame.draw.rect(pygame_screen, WHITE, size, 0)
	rectblack=pygame.draw.rect(pygame_screen, BLACK,size, 2)
	font = pygame.font.SysFont('Inconsolata', font_size)#https://stackoverflow.com/questions/20842801/how-to-display-text-in-pygame download this font from sudo apt-get install fonts-inconsolata
	max_displayed=int(height*0.5/font_size)-1
	text_positions=[(int(width*0.25+5),int(height*0.25+font_size*n+5)) for n in range(0,max_displayed)]
	#main display
	text_regions= [ [[int(width*0.25),int(width*0.65)],[int(height*0.25+font_size*n+5),int(height*0.25+font_size*(n+1)+5)]] for n in range(0,int(height*0.5/font_size))]
	test_temp=["this is a very very very very very very very very very very very very very very very long setence" for n in range(0,20)]
	
	#reading in files
	num_letters=math.floor(38*width/1280)
	f=open("./Menu_Documents/Keyboard_Shortcuts.txt")
	keyboard_shortcut_content=f.readlines()
	f.close()
	keyboard_shortcuts=[["Keyboard Shortcuts","none"],["Back to Main Menu",0]]
	for x in keyboard_shortcut_content:
		keyboard_shortcuts=keyboard_shortcuts+[[x[i:i+num_letters],"none"] for i in range(0, len(x), num_letters)] 
	f=open('./Menu_Documents/Acknowledgments.txt')
	Acknowledgments_content=f.readlines()
	f.close()
	Acknowledgments=[["Acknowledgments","none"],["Back to Main Menu",0]]
	for x in Acknowledgments_content:
		Acknowledgments=Acknowledgments+[[x[i:i+num_letters],"none"] for i in range(0, len(x), num_letters)] 

#https://stackoverflow.com/questions/9475241/split-string-every-nth-character
	Displays=[[["Main Menu","none"],["- Keyboard Shortcuts",1],["- Acknowledgments",2],["- Copyright",3]],keyboard_shortcuts,Acknowledgments,[["Copyright","none"],["Back to Main Menu",0]]]
	scroller_height=lambda n: (height*0.5-4)/(len(Displays[n])-max_displayed+1)
	scroller_positions=[ [ [[width*0.65,width*0.75],[height*0.25+scroller_height(n)*m,height*0.25+scroller_height(n)*(m+1)]] for m in range(0,len(Displays[n])-max_displayed+1)] for n in range(0,len(Displays))]
	if scroller_height(0)>0:
		scroller=pygame.draw.rect(pygame_screen, BLACK,[width*0.65,height*0.25,width*0.1,scroller_height(0)*(1)] ,0)
	current_display=0
	start_index=0
	while True:
		broken=0
		events2 = pygame.event.get() 
		for event2 in events2:
			if event2.type==pygame.KEYDOWN and event2.key == pygame.K_h:
				broken=1
				display_update(pygame_screen)
				break
			if event2.type==pygame.MOUSEBUTTONUP:
				for n in range(0,min(len(Displays[current_display]),max_displayed)):
					mouse = pygame.mouse.get_pos() #
					if Displays[current_display][n][1]!="none" and  text_regions[n][0][0]<mouse[0]<text_regions[n][0][1] and text_regions[n][1][0]<mouse[1]<text_regions[n][1][1]: #change display
						current_display= Displays[current_display][n][1]
						
						rectwhite=pygame.draw.rect(pygame_screen, WHITE, size, 0)
						rectblack=pygame.draw.rect(pygame_screen, BLACK,size, 2)
						if scroller_height(current_display)>0 :
							scroller=pygame.draw.rect(pygame_screen, BLACK,[width*0.65,height*0.25,width*0.1,scroller_height(current_display)] ,0)
						pygame.display.flip()
						start_index=0
						break
				for pos in scroller_positions[current_display]:
					if scroller_height(current_display)>0 and pos[0][0]<mouse[0]<pos[0][1] and pos[1][0]<mouse[1]<pos[1][1]: 
						rectwhite=pygame.draw.rect(pygame_screen, WHITE, size, 0)
						rectblack=pygame.draw.rect(pygame_screen, BLACK,size, 2)
						scroller=pygame.draw.rect(pygame_screen, BLACK,[width*0.65,pos[1][0],width*0.1,scroller_height(current_display)],0)
						pygame.display.flip()
						start_index=scroller_positions[current_display].index(pos)
						
		if broken==1:
			break
		mouse = pygame.mouse.get_pos() #
		n=0
		#for text in Displays[current_display]:
		for n in range(0,min(len(Displays[current_display]),max_displayed)):
			text= Displays[current_display][start_index+n]
			mouse = pygame.mouse.get_pos()
	#https://pythonprogramming.net/making-interactive-pygame-buttons/
			if text[1]!="none" and text_regions[n][0][0]<mouse[0]<text_regions[n][0][1] and text_regions[n][1][0]<mouse[1]<text_regions[n][1][1]: 
				textsurface = font.render(text[0], True, (255, 0, 0))
			else: 
				textsurface = font.render(text[0], True, (0, 0, 0))
			pygame_screen.blit(textsurface,text_positions[n])
			n=n+1
		pygame.display.flip()

def pygame_events(img_display,pygame_screen):
	global continous_or_word_by_word
	events = pygame.event.get() ##https://stackoverflow.com/questions/16044229/how-to-get-keyboard-input-in-pygame
	for event in events:
		if event.type == pygame.KEYDOWN:
			if event.key == pygame.K_p:#pause and unpause
				while True:
					broken=0
					events2 = pygame.event.get() 
					for event2 in events2:
						if event2.type==pygame.KEYDOWN and event2.key == pygame.K_p:
							broken=1
							break
					if broken==1:
						break
			if event.key == pygame.K_h:
				help_menu(pygame_screen)
			if event.key == pygame.K_r:#change voice type
				voice_type=(voice_type+1)%2#i.e. binary addition so 1 or 0
		if event.type==QUIT: #quit from https://www.pygame.org/wiki/WindowResizing
			pygame.display.quit()
			os.system("rm beamer.jpg temp_beamer.pdf temp_beamer.tex temp_pg.pdf")
			quit()
		if event.type==VIDEORESIZE:#resize from https://www.pygame.org/wiki/WindowResizing
				screen=pygame.display.set_mode(event.dict['size'],HWSURFACE|DOUBLEBUF|RESIZABLE)
				screen.blit(pygame.transform.scale(img_display,event.dict['size']),(0,0))
				pygame.display.flip()
	return ""
