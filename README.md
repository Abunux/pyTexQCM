pyTexQCM
--------

Module Python qui contient tout ce qu'il faut pour créer des QCM en LaTeX avec leurs corrections.
Est capable de générer des séries avec les réponses en ordre aléatoire (avec la correction qui va bien ^_^)

Licence CC BY-NC-SA

Frédéric Muller
maths.muller@gmail.com

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






