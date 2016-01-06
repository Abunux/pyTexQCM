#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division

# ——————————————————————————————————————————————————————————————————————————————
#
#								PyTexQCM
#
# ——————————————————————————————————————————————————————————————————————————————
#
# Générateur de QCM en LaTeX avec sauvegardes et imports en XML
#
# ——————————————————————————————————————————————————————————————————————————————
# Projet créé le 2012/05/23
# par Frédéric Muller, aka Abunux
# abunux at gmail dot com
# Licence CC BY-NC-SA
# ——————————————————————————————————————————————————————————————————————————————
VERSION="version 0.1"
# Dernière MAJ : 2015/02/18
# ——————————————————————————————————————————————————————————————————————————————
# TODO :
# ------
# 	- Fichier de configuration pour les constantes (dans un .ini ou un .xml)
#	- Classement des exos (hiérarchie, tags,...)
#	- Possibilité de personnalisations du préambule LaTeX (packages,...)
#	- Ligne de commande pour créer un qcm à partir d'un xml, du type :
#		pytexqcm ds42.xml ——> ds42.pdf
#	- Tests et paramètres sous win$ (et sous MacOS mais j'ai pas…)
#	- Nettoyage du texte avant de le compiler (par ex n° -> \no)
#	- Forcer la position d'une réponse (par ex "Autre réponse" en dernier)
#	- Peut-être "casser" les classes en séparant la structure des questions, le tex, le xml,...
#		(voir héritage et éventuellement réorganisation du code)
#	- Tout ce qui va autour :
#		- Éditeur graphique
#		- Langage de script de création de qcm
#		- Stockage des exos dant une bdd (à voir, chaud à priori)
#		- Réseau : serveur d'exos et client, javascript avec correction auto,...
#		- ... bref y a du boulot...
#
# ——————————————————————————————————————————————————————————————————————————————
# Bugs :
# ------
# - Mineurs :
# 	- Changement de page entre intro exo et 1ère question (pas beau…)
#
# - Majeurs:
#	- Rien pour le moment (mais ça ne saurait tarder…)
#
# ——————————————————————————————————————————————————————————————————————————————

import os,sys
from time import strftime, localtime
from random import *
from math import *
import xml.etree.ElementTree as ET

from texchains import *

# 3 niveaux d'unités :
# ————————————————————
# - TQuestion : une simple question avec réponses justes ou fausses, et barème
# - TExo : une liste de questions avec texte d'intro
# - TDocument : le document .tex final


# ————————————————————— CONSTANTES —————————————————————————————————————————————

if os.name=='posix':
#~ if "linux" in sys.platform : # Sous Linux
	#~ CODAGE='utf8'
	DEFPATH="/tmp"
	PDFLATEX="pdflatex --shell-escape --enable-write18 -synctex=1 -interaction=nonstopmode " # Compilateur LaTex
	PDFREADER="evince " # Lecteur de pdf
	#~ TEXEDITOR="geany " # Éditeur de pdf
	TEXEDITOR="texmaker " # Éditeur de pdf
	FILEMANAGER="nemo " # Explorateur de fichiers
	PDFCROP="pdfcrop " # Couper le pdf (pour preview)
	MV="mv " # Renommer fichier
	CONVERT="convert " # Convertir pdf en image (pour preview)
	

elif os.name=='nt':  # Sous Windows <—— À tester, surement faux…
	# À commenter pour tests sous win$ —————————————————————————#
	print("Système non encore pris en charge")					#
	quit()														#
	# ——————————————————————————————————————————————————————————#
	#~ CODAGE='latin1'
	DEFPATH=r"C:\\"  	# Répertoire tmp ???
	PDFLATEX="pdflatex " # pas sûr… surtout les options
	PDFREADER="acrord32 "
	TEXEDITOR="notepad " # doit y avoir mieux…
	FILEMANAGER="explorer " # Beurk...

else :
	print("Système non supporté")
	quit()

DEFFILENAME="testqcm"


# ————————————————————— Fonctions utiles ———————————————————————————————————————

def maketex(source, preview=False):
	s=""
	s+=TEXPREAMBULE
	if preview :
		s+=r"\pagestyle{empty}"
	else :
		s+=r"\pagestyle{plain}"
	s+=r"\begin{document}"+"\n"
	s+=source+"\n"
	s+=TEXFIN
	return s

def compiletex(source, path=DEFPATH, filename="tmptex", show=True, edit=False, preview=False):
	s=maketex(source,preview)
	pathfile=os.path.join(path, filename)
	f=open(pathfile+".tex","w")
	f.write(s)
	f.close()
	os.system(PDFLATEX+" -output-directory '"+path+"' '"+pathfile+".tex'")
	if show:
		os.system(PDFREADER+" '"+pathfile+".pdf'")
	if edit :
		os.system(TEXEDITOR+" '"+pathfile+".tex'")

def pdfcrop(path=DEFPATH, filename="tmptex", show=True, edit=False):
	pathfile=os.path.join(path, filename)
	os.system(PDFCROP+" '"+pathfile+".pdf'")
	os.system(MV+" '"+pathfile+"-crop.pdf' '"+pathfile+".pdf'")
	if show:
		os.system(PDFREADER+" '"+pathfile+".pdf'")
	if edit :
		os.system(TEXEDITOR+" '"+pathfile+".tex'")

# ————————————————————— class TQuestion ————————————————————————————————————————
class TQuestion:
	def __init__(self,enonce=r"",reponses=[["",False]],alea=False,
				bonus="+1", malus="-0.5", vide="0", col=0,
				filename=DEFFILENAME, path=DEFPATH, tree=None):
		"""enonce : énoncé de la question
reponses : liste des réponses sous la forme d'une liste [[réponse1,juste/faux],[réponse2,juste/faux],...]
alea : True si les réponses sont en ordre aléatoire
bonus, malus, vide : points pour réponse juste, fausse et aucune réponse
col : nbre de colonnes pour les réponses (0 pour autant que de réponses)
tree : ET.Element (XML)"""
		self.enonce=enonce
		self.reponses=reponses
		self.alea=alea		
		self.nbrep=self.get_nbrep()
		
		self.bonus=bonus
		self.malus=malus
		self.vide=vide
		
		self.col=col 	# Nbre de colonnes pour les réponses
		
		self.filename=filename
		self.path=path
		self.tree=tree
		if tree is not None:
			self.parsetree()

# ---------------- Structure  -----------------

	def set_enonce(self,enonce):
		"""Change l'énoncé"""
		self.enonce=enonce

	def add_reponse(self,rep,juste=True):
		"""Ajoute une réponse"""
		self.reponses.append([rep,juste])
		self.nbrep=self.get_nbrep()

	def set_reponse(self,n,rep,juste=True):
		"""Change la réponse n"""
		self.reponses[n-1][0]=rep
		self.reponses[n-1][1]=juste

	def rem_reponse(self,n):
		"""Enlève la réponse n"""
		try:
			self.reponses.pop(n-1)
			self.nbrep=self.get_nbrep()
		except:
			print("Erreur pas de réponse d'indice %d"%(n))

	def get_reponse(self,n):
		"""Retourne la réponse n"""
		return self.reponses[n-1]

	def get_nbrep(self):
		"""Nombre de réponses"""
		self.nbrep=len(self.reponses)
		return len(self.reponses)

	def permute_reponses(self,n,m):
		"""Permute les réponses n et m"""
		rep1=self.get_reponse(n)
		rep2=self.get_reponse(m)
		self.reponses[n-1]=rep2
		self.reponses[m-1]=rep1

	def set_juste(self,n,juste=True):
		"""Met juste (ou faux) la réponse n"""
		self.reponses[n-1][1]=juste

	def set_alea(self,alea=True):
		"""Met l'ordre aléatoire (ou pas)"""
		self.alea=alea

# ---------------- Source LaTex ---------------

	def make_source(self):
		"""Crée le source LaTeX de la question"""
		#~ stretch=1.8
		l=21-2*MARGE 		# Largeur du tableau en cm
		n0=self.get_nbrep()
		if self.col==0:
			n=n0
		else:
			n=self.col
			
		if n!=0:			
			t="%.2fcm"%((l-1)/n) # Largeur d'une "cellule" pour réponse
		else :
			t="%.2fcm"%(l-1) # Largeur d'une "cellule" pour réponse

		self.source=""
		if self.alea:
			shuffle(self.reponses)
		#~ self.source+=r"\renewcommand{\arraystretch}{%.2f}"%(stretch)+"\n"
		#~ self.source+=r"\vspace{-1cm}"+"\n"
		self.source+="\n"
		self.source+=r"% <—— Question ——>"+"\n"
		self.source+="\n"
		self.source+=r"\begin{center}"+"\n"
		self.source+=r"\begin{tabularx}{"+str(l)+r"cm}{p{"+t+r"}*"+str(n-1)+r"X}"+"\n"
		#~ self.source+=r"\hline"+"\n"
		self.source+=r"\multicolumn{"+str(n)+r"}{p{"+str(l)+r"cm}}{"+"\n"
		self.source+=r"\question "+self.enonce+"\n"
		self.source+=r"\rule[-0.4cm]{0cm}{0.4cm}}\\"+"\n"
		#~ self.source+=r"\hline"+"\n"
		
		# Good mais réponses en ligne
		c=65
		for m in range(int(ceil(n0/n))): 
			for k in range(n-1):
				if n*m+k<n0-1:
					self.source+=r"\textbf{"+chr(c)+r" : }"+self.reponses[n*m+k][0]+"&\n"
					c+=1
				elif n*m+k==n0-1:
					self.source+=r"\textbf{"+chr(c)+r" : }"+self.reponses[n*m+k][0]+r"\\"+"\n"
			if n*m+(n-1)<n0:
				self.source+=r"\textbf{"+chr(c)+r" : }"+self.reponses[n*m+(n-1)][0]+r"\\"+"\n"
				c+=1
				
		# Pas bon - Réponses en colonne
		#~ l=int(ceil(n0/n))
		#~ j=0
		#~ for m in range(l): 
			#~ c=65+j
			#~ for k in range(n-1):
				#~ if n*m+k<n0-1:
					#~ self.source+=r"\textbf{"+chr(c)+r" : }"+self.reponses[n*m+k][0]+"&\n"
					#~ c+=l
				#~ elif n*m+k==n0-1:
					#~ self.source+=r"\textbf{"+chr(c)+r" : }"+self.reponses[n*m+k][0]+r"\\"+"\n"
			#~ if n*m+(n-1)<n0:
				#~ self.source+=r"\textbf{"+chr(c)+r" : }"+self.reponses[n*m+(n-1)][0]+r"\\"+"\n"
				#~ c+=l
			#~ j+=1
		
		#~ self.source+=r"\hline"+"\n"
		self.source+=r"\multicolumn{"+str(n)+r"}{p{"+str(l)+r"cm}}{}\\"+"\n"
		self.source+=r"\end{tabularx}"+"\n"
		self.source+=r"\end{center}"+"\n"
		#~ self.source+="\n"
		return self.source

	def make_preview(self, path=DEFPATH, filename="tmptex", show=True, edit=False):
		compiletex(self.make_source(),path,filename,show=False,edit=False,preview=True)
		pdfcrop(path,filename, show, edit)

# ---------------- XML ---------------

	def make_xmltree(self):
		"""Crée le XML de la question"""
		xml=ET.Element("question")
		xml.set("bonus",self.bonus)
		xml.set("malus",self.malus)
		xml.set("vide",self.vide)
		xml.set("alea",str(int(self.alea)))
		xml.set("col",str(self.col))
		xml.set("nbrep",str(self.get_nbrep()))
		xml.text=self.enonce
		for rep in self.reponses:
			xrep=ET.SubElement(xml,"reponse")
			xrep.set("juste",str(int(rep[1])))
			xrep.text=rep[0]
		self.xmlET=xml
		self.tree=ET.ElementTree(xml)
		ET.dump(self.tree)

	def savetoxml(self,fullpath):
		"""Sauve la question dans un XML"""
		self.make_xmltree()
		self.tree.write(fullpath)

	def parsetree(self):
		"""Génère une question à partir d'un XML"""
		elem = self.tree
		self.bonus=elem.get("bonus","+1")
		self.malus=elem.get("malus","-0.5")
		self.vide=elem.get("vide","0")
		self.alea=bool(int(elem.get("alea",False)))
		self.col=int(elem.get("col",0))
		self.nbrep=int(elem.get("nbrep",1))
		self.enonce=elem.text
		self.reponses=[]
		for rep in elem.iter("reponse"):
			self.add_reponse(rep.text,bool(int(rep.get("juste"))))

	def readfromxml(self,fullpath):
		"""Récupère une question à partir d'un XML"""
		self.tree = ET.parse(fullpath)
		self.tree=self.tree.getroot()
		self.parsetree()

# ————————————————————— class TExo —————————————————————————————————————————————
class TExo:
	def __init__(self,liste_questions=[],intro=r"\emph{Les questions de cet exercice sont indépendantes.}",
				alea=False,
				niveau='', chapitre='', tags=[], titre='', description='', index=0,
				newpage=False,
				tree=None):
		"""intro : Enoncé de l'exo
liste_questions : la liste des questions
niveau, chapitre, tags, titre, description, index : pour classer les exos plus tard
newpage : changement de page
tree : ET.Element (XML)"""
		self.intro=intro
		
		self.liste_questions=liste_questions
		self.alea=alea
		
		self.niveau=niveau
		self.chapitre=chapitre
		self.tags=tags
		self.titre=titre
		self.description=description
		self.index=index
		
		self.newpage=newpage
		
		self.tree=tree
		if tree is not None:
			self.parsetree()

# ---------------- Structure  -----------------

	def set_intro(self,intro):
		"""Écrit l'énoncé"""
		self.intro=intro

	def get_question(self,n):
		"""Retourne la n-ième question"""
		return self.liste_questions[n-1]

	def permute_questions(self,n,m):
		"""Permute les questions n et m"""
		q1=self.get_question(n)
		q2=self.get_question(m)
		self.liste_questions[n-1]=q2
		self.liste_questions[m-1]=q1

	def insert_question(self,question,n=0):
		"""Insert une question à la position n"""
		if n>0: # Position n
			self.liste_questions=self.liste_questions[:n-1]+[question]+self.liste_questions[n-1:]
		else:   # Sinon à la fin
			self.liste_questions+=[question]

	def set_alea(self,alea=True):
		"""Met les réponses en ordre aléatoire"""
		for q in self.liste_questions:
			q.set_alea(alea)

	def max_nbrep(self):
		"""Nombre de réponse maximum de la liste de questions"""
		m=0
		for q in self.liste_questions:
			if len(q.reponses)>m : m=len(q.reponses)
		return m

	def nb_questions(self):
		"""Nombre de questions de l'exo"""
		return len(self.liste_questions)

	def bareme(self):
		"""Nombre total de points de l'exo"""
		p=0
		for q in self.liste_questions:
			p+=eval(q.bonus)
		return p

# ---------------- Source LaTex ---------------

	def make_source(self):
		"""Source LaTeX de l'énoncé"""
		self.source=r"\exercice \textbf{\hfill "+str(self.bareme())+" points}\par"+"\n"
		#~ if self.newpage :
			#~ self.source+=r"\tournerpage"+"\n"
		if self.intro:
			self.source+=r"\par "+self.intro+"\n"
			self.source+=r"\nopagebreak"+"\n"
		for quest in self.liste_questions:
			quest.make_source()
			self.source+=quest.source
		self.source+="\n"
		return self.source

	def make_srctabrep(self,correction=False):
		"""Source LaTeX du tableau de réponses, et de la correction"""
		if correction :
			coul=r"\cellcolor{gris2}"
		else:
			coul=""
		m=self.max_nbrep()
		n=self.nb_questions()
		p=self.bareme()
		self.srctabrep=""
		#~ self.srctabrep+=r"\exercice"+"\n"
		self.srctabrep+=r"\vspace{\baselineskip}"+"\n"
		self.srctabrep+=r"\begin{tabular}{|c"+r"|c"*m+r"|>{\columncolor{gris1}}c|>{\columncolor{gris1}}c|>{\columncolor{gris1}}c|}"+"\n"
		self.srctabrep+=r"\multicolumn{"+str(m+4)+r"}{l}{\exercice}\\"+"\n"
		self.srctabrep+=r"\hline"+"\n"
		c=65
		self.srctabrep+=r"&"
		for k in range(m):
			self.srctabrep+=r"\textbf{"+chr(c)+"}&"
			c+=1
		self.srctabrep+=r"Juste&Faux&Vide\\"+"\n"
		self.srctabrep+=r"\hline"+"\n"

		for k in range(n):
			self.srctabrep+=r"\textbf{Q%d}&"%(k+1)
			t=0
			for j in range(len(self.liste_questions[k].reponses)):
				if self.liste_questions[k].reponses[j][1]:
					self.srctabrep+=coul+"&"
				else:
					self.srctabrep+=r"&"
				t+=1
			self.srctabrep+=r"\cellcolor{black}&"*(m-t)
			self.srctabrep+="%s&%s&%s"%(self.liste_questions[k].bonus,self.liste_questions[k].malus,self.liste_questions[k].vide)
			self.srctabrep+=r"\\"+"\n"
			self.srctabrep+=r"\hline"+"\n"
		#~ self.srctabrep+=r"\multicolumn{"+str(m+1)+r"}{|c|}{\cellcolor{gris1} Total}&&&\\"+"\n"
		#~ self.srctabrep+=r"\hline"+"\n"
		self.srctabrep+=r"\hline"+"\n"
		self.srctabrep+=r"\multicolumn{"+str(m+1)+r"}{|c|}{\cellcolor{gris1}\textbf{Total :}}&\multicolumn{3}{|r|}{\cellcolor{gris1}\textbf{/"+str(p)+r"}}\rule[-0.5cm]{0cm}{1cm}\\"+"\n"
		self.srctabrep+=r"\hline"+"\n"+r"\end{tabular}"+"\n"
		#~ self.srctabrep+=r"\vspace{\baselineskip}"+"\n"
		self.srctabrep+="\n"
		return self.srctabrep

	def make_preview(self, path=DEFPATH, filename="tmptex", show=True, edit=False):
		compiletex(self.make_source(),path,filename,show=False,edit=False, preview=True)
		pdfcrop(path,filename, show, edit)

# ---------------- XML ---------------

	def make_xmltree(self):
		"""Crée le XML de l'exo"""
		xml=ET.Element("exo")
		xml.set("niveau",self.niveau)
		xml.set("chapitre",self.chapitre)
		xml.set("titre",self.titre)
		xml.set("description",self.description)
		xml.set("index",str(self.index))
		xml.set("newpage",str(int(self.newpage)))
		xml.set("alea",str(int(self.alea)))
		xml.text=self.intro
		for quest in self.liste_questions:
			quest.make_xmltree()
			xml.append(quest.xmlET)
		self.xmlET=xml
		self.tree=ET.ElementTree(xml)
		ET.dump(self.tree)

	def savetoxml(self,fullpath):
		"""Sauve l'exo dans un XML"""
		self.make_xmltree()
		self.tree.write(fullpath)

	def parsetree(self):
		"""Génère un exo à partir d'un XML"""
		elem = self.tree
		self.niveau=elem.get("niveau","")
		self.chapitre=elem.get("chapitre","")
		self.titre=elem.get("titre","")
		self.description=elem.get("description","")
		self.index=elem.get("index",0)
		self.alea=bool(int(elem.get("alea",False)))
		self.intro=elem.text
		self.liste_guestions=[]
		for quest in elem.iter("question"):
			Q=TQuestion(reponses=[],tree=quest)
			self.insert_question(Q)

	def readfromxml(self,fullpath):
		"""Récupère un exo à partir d'un XML"""
		self.tree = ET.parse(fullpath)
		self.tree = self.tree.getroot()
		self.parsetree()

# ————————————————————— class TDocument ————————————————————————————————————————
class TDocument:
	def __init__(self,liste_exos=[],
				titre='', numds=1, theme="Tests",sujet=-1, consignes_gen=CONSIGNES_GEN, calculatrice=True, duree="1 heure", classe="2nde",				
				path=DEFPATH, filename='', compil=False, show=True, edit=False, correction=True):
		"""liste_exos: la liste des exos du qcm
titre, consignes_gen, calculatrice, duree, classe : info de la cartouche
sujet : Sujet A, B, C,... si sujet=-1, alors un seul sujet
theme : thème du DS
numds : numéro du DS
path, filename : chemin et nom de fichier
compil, show, edit : compiler le .tex, voir le résultat, éditer le .tex"
correction : ajouter la fiche avec les corrections"""
		self.liste_exos=liste_exos
		if titre:
			self.titre=titre
		else : 
			self.titre=r"DS \no%d"%(numds)
		self.numds=numds
		self.theme=theme
		self.sujet=sujet
		self.duree=duree
		self.classe=classe
		self.calculatrice=calculatrice
		
		self.consignes_gen=consignes_gen
		
		self.basepath=path
		self.path=path
		#~ self.basefilename=filename
		#~ self.filename=filename
		if not filename :
			if titre :
				self.basefilename="%s-%s-%s"%(self.classe, self.titre.replace(' ','').replace('n°','').replace(r'\no',''), self.theme)
				self.filename="%s-%s-%s"%(self.classe, self.titre.replace(' ','').replace('n°','').replace(r'\no',''), self.theme)
			else :
				self.basefilename="%s-DS%.2d-%s"%(self.classe, self.numds, self.theme)
				self.filename="%s-DS%.2d-%s"%(self.classe, self.numds, self.theme)
		else :
			self.basefilename=filename
			self.filename=filename
		self.pathfile=os.path.join(self.path, self.filename)
		
		self.correction=correction
		self.compil=compil # Compile le doc à la création
		self.show=show
		self.edit=edit
		
		self.make_source(self.compil)

# ---------------- Gestion fichier  -----------------

	def change_path(self,path):
		self.path=path
		self.pathfile=os.path.join(self.path, self.filename)

	def change_filename(self,filename):
		self.filename=filename
		self.pathfile=os.path.join(self.path, self.filename)

	def restore_pathfile(self):
		self.path=self.basepath
		self.filename=self.basefilename

	def change_basepath(self,path):
		self.basepath=path
		self.path=path
		self.pathfile=os.path.join(self.path, self.filename)

	def change_basefilename(self,filename):
		self.basefilename=filename
		self.filename=filename
		self.pathfile=os.path.join(self.path, self.filename)

# ---------------- Structure  -----------------

	def get_exo(self,n):
		"""Retourne le n-ième exo"""
		return self.liste_exos[n-1]

	def permute_exos(self,n,m):
		"""Permute les exos n et m"""
		e1=self.get_exo(n)
		e2=self.get_exo(m)
		self.liste_exos[n-1]=e2
		self.liste_exos[m-1]=e1

	def insert_exo(self,exo,n=0):
		"""Insert un exo à la position n"""
		if n>0: # Position n
			self.liste_exos=self.liste_exos[:n-1]+[exo]+self.liste_exos[n-1:]
		else:   # Sinon à la fin
			self.liste_exos+=[exo]

	def nb_questions(self):
		"""Nombre total de questions dans le QCM"""
		q=0
		for exo in self.liste_exos:
			q+=exo.nb_questions()
		return q

	def nb_exos(self):
		"""Nombre d'exos dans le QCM"""
		return len(self.liste_exos)

	def bareme(self):
		""" Nombre total de points"""
		p=0
		for exo in self.liste_exos:
			p+=exo.bareme()

# ---------------- Source LaTex ---------------

	def make_source_preambule(self):
		self.source+=r"% ——————————————————————————————————————————————————————————————————————————————"+"\n"
		self.source+=r"%"+"\n"
		self.source+=r"%           Document créé avec pytexqcm le "+strftime("%d/%m/%Y à %Hh%M",localtime())+"\n"
		self.source+=r"%"+"\n"
		self.source+=r"%  F.Muller - abunux at gmail dot com"+"\n"
		self.source+=r"%  Licence CC BY-NC-SA"+"\n"
		self.source+=r"%"+"\n"
		self.source+=r"% ——————————————————————————————————————————————————————————————————————————————"+"\n"
		self.source+="\n"
		self.source+=TEXPREAMBULE
		self.source+="\n"
		self.source+=r"\begin{document}"+"\n"
		self.source+="%<—————————————————————————————————————————————————————————————————————————————>"+"\n"
		self.source+="%                  Début du document"+"\n"
		self.source+="%<—————————————————————————————————————————————————————————————————————————————>"+"\n"

	def make_source_cartouche(self):
		"""Cartouche pour l'énoncé"""
		self.source+=r"\begin{center}"+"\n"
		self.source+=r"\begin{tabular}{|p{.85\linewidth}|p{.15\linewidth}|}\hline"+"\n"
		self.source+="Durée : " + self.duree + "&\multicolumn{1}{r|}{" + self.classe + r"}\\"+"\n"
		self.source+="\hline"+"\n"
		self.titre=self.titre.replace("°",r"\textsuperscript{o}")
		self.source+=r"\multicolumn{2}{|c|}{}\\"+"\n"
		self.source+=r"\multicolumn{2}{|c|}{\textbf{\LARGE{" + self.titre + r"}}}\\"+"\n"
		if self.sujet !=-1 :
			self.source+=r"\multicolumn{2}{|r|}{\textbf{Sujet " + chr(65+self.sujet) + r"}}\\"+"\n"
		else :
			self.source+=r"\multicolumn{2}{|r|}{}\\"+"\n"
		self.source+=r"\hline"+"\n"
		if self.calculatrice:
			self.source+=r"\multicolumn{2}{|c|}{Calculatrice autorisée. Aucun autre document n'est autorisé.} \\"+"\n"
		else:
			self.source+=r"\multicolumn{2}{|c|}{Calculatrice NON autorisée. Aucun document n'est autorisé.} \\"+"\n"
		self.source+=r"\hline"+"\n"
		self.source+=r"\end{tabular}"+"\n"
		self.source+=r"\end{center}"+"\n"
		self.source+="\n"
		if self.consignes_gen:
			self.source+=self.consignes_gen + r"\\"+"\n"
		self.source+="%<—————————————————————————————————————————————————————————————————————————————>"+"\n"

	def make_source_cartouche2(self):
		"""Cartouche pour la fiche réponse"""
		self.source+=r"\setcounter{numexo}{0}"+"\n"
		self.source+=r"\begin{center}"+"\n"
		self.source+=r"\begin{tabular}{|p{.85\linewidth}|p{.15\linewidth}|}\hline"+"\n"
		self.source+=r"NOM - PRÉNOM : & Classe :\\"+"\n"
		self.source+=r"&\\"+"\n"
		self.source+=r"&\\"+"\n"
		self.source+=r"\hline"+"\n"
		self.titre=self.titre.replace("°",r"\textsuperscript{o}")
		self.source+=r"\multicolumn{2}{|c|}{}\\"+"\n"
		self.source+=r"\multicolumn{2}{|c|}{\textbf{\LARGE{" + self.titre + r"}}}\\"+"\n"
		self.source+=r"\multicolumn{2}{|c|}{\textbf{\Large{Fiche réponse à rendre}}}\\"+"\n"
		if self.sujet !=-1 :
			self.source+=r"\multicolumn{2}{|r|}{\textbf{Sujet " + chr(65+self.sujet) + r"}}\\"+"\n"
		else :
			self.source+=r"\multicolumn{2}{|r|}{}\\"+"\n"
		self.source+=r"\hline"+"\n"
		self.source+=r"\multicolumn{2}{|l|}{}\\"+"\n"
		self.source+=r"\multicolumn{2}{|l|}{\hspace{1cm}\textbf{\LARGE{Note finale :}}}\\"+"\n"
		self.source+=r"\multicolumn{2}{|l|}{}\\"+"\n"
		self.source+=r"\hline"+"\n"
		self.source+=r"\end{tabular}"+"\n"
		self.source+=r"\end{center}"+"\n"
		self.source+="\n"
		self.source+=r"\begin{center}"+"\n"
		self.source+=r"\emph{Cochez la bonne réponse – Ne rien écrire dans les cases grisées}"+"\n"
		self.source+=r"\end{center}"+"\n"
		self.source+="%<—————————————————————————————————————————————————————————————————————————————>"+"\n"
		self.source+="\n"

	def make_source_exos(self):
		numexo=1
		for exo in self.liste_exos:
			self.source+="\n"
			self.source+=r"% <———————— Exo ————————>"+"\n"
			self.source+="\n"
			if exo.newpage and numexo!=1:
				self.source+=r"\tournerpage"+"\n"
			#~ self.source+=r"\exercice \textbf{\hfill "+str(exo.bareme())+" points}\par"+"\n"
			self.source+=r"\nopagebreak"+"\n"
			exo.make_source()
			self.source+=exo.source
			numexo+=1

	def make_source_ficherep(self,correction=False):
		self.source+="%<—————————————————————————————————————————————————————————————————————————————>"+"\n"
		if correction:
			self.source+="%                 Correction"+"\n"
		else:
			self.source+="%                Fiche réponse"+"\n"
		self.source+="%<—————————————————————————————————————————————————————————————————————————————>"+"\n"

		n=self.nb_questions()
		e=self.nb_exos()
		if e*7.5+n>45:
			multicol=True
		else:
			multicol=False

		self.source+=r"\renewcommand{\arraystretch}{1}"+"\n"
		self.source+=r"\newpage"+"\n"
		self.make_source_cartouche2()
		if multicol:
			self.source+=r"\begin{multicols}{2}"
		for exo in self.liste_exos:
			exo.make_srctabrep(correction)
			self.source+=exo.srctabrep
		if multicol:
			self.source+=r"\end{multicols}"

	def make_source_fin(self):
		self.source+=TEXFIN

	def make_source(self,compil=True):
		"""Source du document final"""
		self.source=""
		self.make_source_preambule()
		self.make_source_cartouche()
		self.make_source_exos()
		self.make_source_ficherep(correction=False)
		if self.correction :
			self.make_source_ficherep(correction=True)
		self.make_source_fin()
		print(self.source)
		if compil:
			self.compile_document()
		return self.source

	def make_preview(self,n,show=True, edit=False):
		"""Preview de l'exo n"""
		self.liste_exos[n-1].make_preview(self.path, self.filename+" - Preview Exo"+str(n),show,edit)

# ---------------- Compilation ---------------

	def make_tex(self):
		"""Crée le .tex"""
		f=open(self.pathfile+".tex","w")
		f.write(self.source)
		f.close()

	def compile_tex(self):
		"""Compile le .tex"""
		os.system(PDFLATEX+" -output-directory '"+self.path+"' '"+self.pathfile+".tex'")

	def show_pdf(self):
		"""Visualise le .pdf"""
		os.system(PDFREADER+" '"+self.pathfile+".pdf'")

	def edit_tex(self):
		"""Edite le .tex"""
		os.system(TEXEDITOR+" '"+self.pathfile+".tex'")

	def compile_document(self):
		"""Crée le .tex, le compile et sort un .pdf"""
		self.make_tex()
		self.compile_tex()
		if self.show:
			self.show_pdf()
		if self.edit:
			self.edit_tex()

	def make_serie(self,n=1):
		"""Crée une série de n sujets avec odre des réponses aléatoire
		   En fait, un peu le but de ce programme..."""
		for exo in self.liste_exos:
			exo.set_alea(True)
		self.show=False
		self.compil=True
		for i in range(n):
			self.change_filename(self.basefilename+"-"+chr(i+65))
			self.sujet=i
			self.make_source()
			self.restore_pathfile()

# ---------------- XML ---------------

	def make_xmltree(self):
		"""Crée le XML du qcm"""
		xml=ET.Element("document")
		xml.set("titre",self.titre)
		xml.set("numds",str(self.numds))
		xml.set("sujet",str(self.sujet))
		xml.set("duree",self.duree)
		xml.set("classe",self.classe)
		xml.set("consignes_gen",self.consignes_gen)
		xml.set("calculatrice",str(int(self.calculatrice)))
		xml.set("theme",self.theme)
		for exo in self.liste_exos:
			exo.make_xmltree()
			xml.append(exo.xmlET)
		self.xmlET=xml
		self.tree=ET.ElementTree(xml)
		ET.dump(self.tree)

	def savetoxml(self,fullpath):
		"""Sauve le qcm dans un XML"""
		self.make_xmltree()
		self.tree.write(fullpath)

	def parsetree(self):
		"""Génère un qcm à partir d'un XML"""
		elem = self.tree
		self.titre=elem.get("titre","")
		self.numds=int(elem.get(self.numds,1))
		self.sujet=int(elem.get("sujet",0))
		self.duree=elem.get("duree","")
		self.classe=elem.get("classe","")
		self.consignes_gen=elem.get("consignes_gen",CONSIGNES_GEN)
		self.calculatrice=bool(int(elem.get("calculatrice",True)))
		self.theme=elem.get("theme","")
		self.list_exos=[]
		for exo in elem.iter("exo"):
			E=TExo(liste_questions=[],tree=exo)
			self.insert_exo(E)

	def readfromxml(self,fullpath):
		"""Récupère un qcm à partir d'un XML"""
		self.tree = ET.parse(fullpath)
		self.tree = self.tree.getroot()
		self.parsetree()

# ————————————————————— main program (tests) ———————————————————————————————————
def main():

	# ==========================================================================
	# 								Tests
	# ==========================================================================

	# Génération de questions
	# -----------------------
	enonce=r"Quelle est la couleur du cheval blanc d'Henri IV ?"
	reponses=[["Pommelé",0],["Blanc",1], ["Noir",0], ["Gris",0]]
	Q1=TQuestion(enonce,reponses,alea=False)
	#~ Q1.make_preview()

	enonce=r"Combien font $2+2$ ?"
	reponses=[["3",0],["1",0], ["4",1], ["5",0]]
	Q2=TQuestion(enonce,reponses,bonus="+2",malus="-1")

	enonce=r"Combien font $3\times5$ ?"
	reponses=[["-15",0],["2",0], ["8",0], ["15",1]]
	Q3=TQuestion(enonce,reponses)

	enonce=r"Combien de choix a cette question ? "
	reponses=[["1",0],["2",0], ["3",1]]
	Q4=TQuestion(enonce,reponses)

	enonce=r'Vrai ou faux : «La réponse à cette question est "Vrai"» '
	reponses=[["Vrai",1],["Faux",0]]
	Q5=TQuestion(enonce,reponses)
	Q5.add_reponse("Peut-être",False)

	enonce=r"5 choix possibles pour celle-ci, juste pour voir… "
	reponses=[["Pas bon",0],["Pas bon",0],["Pas bon",0],["Bon",1],["Pas bon",0]]
	Q6=TQuestion(enonce,reponses,col=4)

	enonce=r"Parmi les propositions suivantes, quelle est celle qui permet d'affirmer que la fonction exponentielle  admet pour asymptote la droite d'équation $y = 0$ ?"
	Q7=TQuestion(enonce,[])
	Q7.add_reponse(r"$\displaystyle\lim_{x \to +\infty} \text{e}^x = + \infty$",False)
	Q7.add_reponse(r"$\displaystyle\lim_{x \to -\infty} \text{e}^x = 0$",True)
	Q7.add_reponse(r"$\displaystyle\lim_{x \to +\infty} \dfrac{\text{e}^x}{x} = + \infty$",False)

	enonce=r"Combien vaut $\cos{\cfrac{\pi}{4}}$ ?"
	Q8=TQuestion(enonce,[])
	Q8.add_reponse(r"$\cfrac{\sqrt{2}}{2}$",True)
	Q8.add_reponse(r"$-\cfrac{\sqrt{2}}{2}$",False)
	Q8.add_reponse(r"$\cfrac{1}{2}$",False)
	Q8.add_reponse(r"$\cfrac{\sqrt{3}}{2}$",False)

	enonce=r"Comment ça va ?"
	Q9=TQuestion(enonce,[],col=2)
	Q9.add_reponse(r"Bien mais pas top enfin ça dépend",False)
	Q9.add_reponse(r"Pas top quoique ça pourrait le faire s'il faisait beau",False)
	Q9.add_reponse(r"Génial tout roule, la super pèche d'enfer",True)
	Q9.add_reponse(r"En quoi ça vous regarde, je tiens à garder un minimum de vie privée",False)

	# Génération d'exos
	# -----------------
	E1=TExo(intro="Quelques questions en vrac :",liste_questions=[Q1,Q2],niveau="2nde",chapitre="trigo")
	E1.insert_question(Q3)
	#~ E1.make_preview()

	E2=TExo(liste_questions=[Q3,Q4,Q5,Q6,Q7,Q8,Q9],newpage=True)
	E2.permute_questions(2,4)

	E3=TExo(intro="",liste_questions=[Q1]*40)
	E4=TExo(liste_questions=[Q5]*5)
	E5=TExo(liste_questions=[Q2,Q7,Q8,Q9])

	E6=TExo([])
	E6.insert_question(Q1)
	E6.insert_question(Q2)
	E6.insert_question(Q8)

	E7=TExo([])
	E7.insert_question(Q3)
	E7.insert_question(Q4)
	E7.insert_question(Q5)

	# ——————————————————————————————————————————————————————————————————————————
	# 			Tests Compilation LaTeX
	# ——————————————————————————————————————————————————————————————————————————

	# Test principal
	# --------------
	#~ doc=TDocument([E1,E2],numds=1,compil=True,show=True,edit=False)

	# Cas extrèmes
	# ------------
	#~ doc=TDocument([E2]*10,titre="DS n°42",compil=True,show=True)
	#~ doc=TDocument([E1]*5+[E3],titre="DS n°42",compil=True,show=True)

	# Création d'un doc "à la main"
	# -----------------------------
	#~ doc=TDocument([],titre="DS n°42",edit=True,show=True)
	#~ doc.insert_exo(E6)
	#~ doc.insert_exo(E7)
	#~ doc.insert_exo(E4,2)
	#~ doc.make_source()

	# Autres fonctionnalités
	# ----------------------
	#~ doc=TDocument([E1,E2],titre="DS n°42")
	#~ doc.make_preview(2)

	# Série de 4 sujets avec réponses aléatoires (trop bon !!!)
	# ---------------------------------------------------------
	doc=TDocument([E1,E2],titre="DS n°42")
	doc.make_serie(4)
	os.system(FILEMANAGER+doc.path)

	# ——————————————————————————————————————————————————————————————————————————
	# 			Tests XML
	# ——————————————————————————————————————————————————————————————————————————

	# Écriture
	# --------
	#~ Q1.savetoxml("testxml_quest")
	#~ os.system("geany testxml_quest.xml")

	#~ E1.savetoxml("testxml_exo")
	#~ os.system("geany testxml_exo.xml")

	#~ doc=TDocument([E1,E2],titre="DS n°42")
	#~ doc.savetoxml("testxml_doc")
	#~ os.system("geany testxml_doc.xml")

	# Lecture
	# -------
	#~ Q=TQuestion([])
	#~ Q.readfromxml("testxml_quest")
	#~ E=TExo([Q])
	#~ doc=TDocument([E],titre="DS n°42",compil=True,show=True)

	#~ E=TExo([])
	#~ E.readfromxml("testxml_exo")
	#~ doc=TDocument([E],titre="DS n°42",compil=True,show=True)

	#~ doc=TDocument([])
	#~ doc.readfromxml("testxml_doc")
	#~ doc.make_source()


	return 0

if __name__ == '__main__':
	main()

