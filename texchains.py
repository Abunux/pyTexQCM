#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Module texchains de pytexqcm
# Contient les chaînes constantes LaTeX pour la compilation :

import sys

if "linux" in sys.platform : # Sous Linux
	CODAGE='utf8'

elif os.name=='nt':  # Sous Windows <—— À tester, surement faux…
	# À commenter pour tests sous win$ —————————————————————————#
	print("Système non encore pris en charge")					#
	quit()														#
	# ——————————————————————————————————————————————————————————#
	

else :
	print("Système non supporté")
	quit()

TAILLEFONT=11
MARGE=1.5

TEXPREAMBULE=r"""
\PassOptionsToPackage{table}{xcolor}
\documentclass["""+str(TAILLEFONT)+r"""pt,a4paper]{article}"""+"\n"


TEXPREAMBULE+=r"""
\usepackage["""+CODAGE+r"""]{inputenc}						% Encodage français
\usepackage[frenchb]{babel}						% Mise en forme française
\usepackage[T1]{fontenc}						% Encodage caractères français

\usepackage{fourier}							% Différents symboles et polices
\usepackage[scaled=0.875]{helvet}				% Font générale
\usepackage{courier}							% Font télétype
\renewcommand{\ttdefault}{lmtt}					% Font télétype
%\usepackage{lmodern}							% Police Latin Modern
\usepackage{frcursive}							% Ecriture manuscrite type écolier
\usepackage{calligra}							% Ecriture manuscrite classieuse
\usepackage{verbatim}							% Commentaires

\usepackage{amsfonts,amsmath,amssymb}			% Symboles maths
\usepackage{bm}									% Symboles maths en gras \bm{}
\usepackage{amstext}							% Texte en mode math de taille adaptée
\usepackage{amsopn}								% \DeclareMathOperator
\usepackage{mathrsfs}							% Symboles maths
\usepackage{mathtools}							% Symboles maths
\usepackage{theorem}							% Mise en forme des théorèmes

\usepackage{textcomp}							% Symboles
\usepackage{pifont}								% Symboles "ding"
\usepackage{wasysym}							% Symboles (smiley et logos)
\usepackage{epsdice}							% Symboles (faces d'un dé)
\usepackage[normalem]{ulem}						% Fioritures de texte (barré, etc...)
\usepackage{cancel}								% Barrer du texte (simplifier termes)
\usepackage{fancybox}							% Boîtes

\usepackage{tabularx, array}					% Tableaux évolués
\usepackage{longtable}							% Tableaux sur plusieurs pages
\usepackage{diagbox}							% Cases en diagonale
%~ \usepackage{tabls}							% Espaces dans les tableaux (conflit avec bclogo)
\usepackage{multirow}							% Fusionner les lignes d'un tableau
\usepackage{enumerate}							% Enumérations personnalisées
\usepackage{multicol}							% Environnement multicolonnes
\usepackage{fancyhdr}							% En-têtes et pieds de page

\usepackage[usenames, dvipsnames]{xcolor}		% Couleurs
%\usepackage{graphicx}							% Insérer des images
\usepackage{pgf, tikz, tkz-tab, tkz-fct}		% Graphiques avec Tikz
\usetikzlibrary{arrows}
\usetikzlibrary{snakes}
\usepackage{alterqcm}							% QCM
\usepackage{circuitikz}							% Circuit éléctriques
\usepackage[tikz]{bclogo}						% Boites à logo

\usepackage{titlesec}							% Mise en forme des titres de sections
\usepackage{fullpage}							% Remplit la page
\usepackage{lastpage}							% Dernière page : \pageref{LastPage}
\usepackage[margin="""+str(MARGE)+r"""cm]{geometry}"""+"\n"


TEXPREAMBULE+=r"""
\renewcommand{\headrulewidth}{0pt}
\renewcommand \footrulewidth{.2pt}
%\pagestyle{plain}
%\everymath{\displaystyle\everymath{}}		% Toutes les équations en mode \displaystyle
\everymath{\displaystyle}
\DecimalMathComma							% Virgule comme séparateur décimal
\frenchspacing								% Espaces français
\setlength{\parindent}{0pt}					% """+"\n"


TEXPREAMBULE+=r"""
\newcounter{numexo}
\newcommand{\exercice}
{\par\vspace{\baselineskip}\noindent\stepcounter{numexo}\textbf{Exercice \arabic{numexo}}}

\newcounter{numquest}[numexo]
\newcommand{\question}
{\par\noindent\stepcounter{numquest}\textbf{\large{Q\arabic{numquest} : }}}

\definecolor{gris1}{gray}{0.8}
\definecolor{gris2}{gray}{0.5}"""+"\n"

TEXPREAMBULE+=r"""
\newcommand{\euro}{\eurologo{}}
\newcommand{\R}{\ensuremath{\mathbb{R}}}
\newcommand{\N}{\ensuremath{\mathbb{N}}}
\newcommand{\D}{\ensuremath{\mathbb{D}}}
\newcommand{\Z}{\ensuremath{\mathbb{Z}}}
\newcommand{\Q}{\ensuremath{\mathbb{Q}}}
\newcommand{\C}{\ensuremath{\mathbb{C}}}
\newcommand{\e}{\text{e}}
\renewcommand{\i}{\text{i}}
\newcommand{\s}{\ensuremath{\mathcal{S}}}
\newcommand{\sol}[1]{\mathcal{S}=\left\lbrace #1 \right\rbrace}
\newcommand{\ou}{\mbox{ ou }}
\newcommand{\et}{\mbox{ et }}
\newcommand{\si}{\mbox{ si }}
\newcommand{\Df}{\ensuremath{\mathcal{D}_f}}
\newcommand{\Cf}{\ensuremath{\mathcal{C}_f}}
\newcommand{\Dg}{\ensuremath{\mathcal{D}_g}}
\newcommand{\Cg}{\ensuremath{\mathcal{C}_g}}

\renewcommand{\P}{\ensuremath{\text{P}}}
\newcommand{\card}{\text{card}}
\newcommand{\E}{\text{E}}
\newcommand{\V}{\text{V}}

\newcommand{\FI}{\textbf{F.I.}}

\newcommand{\eq}{\ \Leftrightarrow\ } % ou \iff
\newcommand{\implique}{\Rightarrow}
\newcommand{\pheq}{\phantom{\eq}}
\newcommand{\egdef}{\stackrel{\textit{déf}}{=}}

\renewcommand{\ge}{\geqslant}
\renewcommand{\le}{\leqslant}
\newcommand{\supeg}{\geqslant}
\newcommand{\infeg}{\leqslant}

\newcommand{\lacco}{\left\lbrace}
\newcommand{\racco}{\right\rbrace}
\newcommand{\labs}{\left|}
\newcommand{\rabs}{\right|}

\newcommand{\inclus}{\subset}
\newcommand{\ninclus}{\not\subset}
\newcommand{\union}{\cup}
\newcommand{\inter}{\cap}

\newcommand{\non}[1]{\text{non(}#1\text{)}}

\newcommand{\dx}{~\text{d}x}
\newcommand{\dt}{~\text{d}t}

\renewcommand{\Re}{\text{Re}}
\renewcommand{\Im}{\text{Im}}
\newcommand{\conj}[1]{\overline{#1}}
\newcommand{\abs}[1]{|#1|}

\newcommand{\pinf}{+\infty}
\newcommand{\minf}{-\infty}
\newcommand{\pminf}{\pm\infty}

\newcommand{\para}{\ /\!\!/\ }

\newcommand{\comb}[2]{\text{C}_{#1}^{#2}}

\newcommand{\vect}[1]{\mathchoice
	{\overrightarrow{\displaystyle\mathstrut#1\,\,}}
	{\overrightarrow{\textstyle\mathstrut#1\,\,}}
	{\overrightarrow{\scriptstyle\mathstrut#1\,\,}}
	{\overrightarrow{\scriptscriptstyle\mathstrut#1\,\,}}}

\def\Oij{$\left(\text{O},~\vect{i},~\vect{j}\right)$}
\def\Oijk{$\left(\text{O},~\vect{i},~ \vect{j},~ \vect{k}\right)$}
\def\Ouv{$\left(\text{O},~\vect{u},~\vect{v}\right)$}

\newcommand{\vu}{\vect{u}}
\newcommand{\vv}{\vect{v}}
\newcommand{\vw}{\vect{w}}
\newcommand{\vn}{\vect{n}}

\newcommand{\veccol}[3]{\left(\begin{array}{c}
{#1}\\{#2}\\{#3}
\end{array}\right)}

\newcommand{\fct}[5]{
	\begin{array}[t]{r ccl}
	{#1}\ : \ &{#2}&\longrightarrow&{#3}\\
	&{#4}&\longmapsto&{#5}
	\end{array}}

\newcommand{\suit}{\begin{tikzpicture}
\draw[color=white](-0.4em,0em)--(-0.25em,0em);
\draw ((-0.25em,-0.15em)--(0.07em,0.18em);
\draw (0.07em,0.18em) arc (135:0:0.25em);
\draw (0.5em,0em) arc (-180:-45:0.25em);
\draw (0.93em,-0.18em)--(1.36em,0.25em);
\draw (1.01em,0.25em)--(1.36em,0.25em)--(1.36em,-0.1em);
\draw[color=white](1.40em,0em)--(1.55em,0em);
\end{tikzpicture}}

% --------------------- \systlin ----------------------------------------
% Système linéaire 2*2
% Paramètres : a, ±b, c, a', ±b', c'
%
\newcommand{\systlin}[6]{
$\left\lbrace
\begin{array}{r @{x~} l @{y~=~} l l}
#1&#2&#3&(L_1)\\
#4&#5&#6&(L_2)
\end{array}
\right.$
}

\def\tournerpage{\vfill%
	\begin{flushright}	
		\textbf{Tourner la page }$\mathbf{\rightarrow}$
	\end{flushright}
	\newpage}


\renewcommand{\sum}{\displaystyle \sum}

"""+"\n"


TEXFIN=r"""\end{document}"""

CONSIGNES_GEN=r"""\emph{Ce devoir est un QCM.\\
Pour chaque question, une seule réponse est juste. L'ordre des réponses est aléatoire.\\
\textbf{Cochez la bonne réponse sur la fiche réponse jointe sur laquelle vous aurez indiqué \large{votre NOM et votre CLASSE}.}
Le barème est indiqué sur cette dernière.
Pas de total négatif par exercice. Aucune justification n'est demandée.}"""
