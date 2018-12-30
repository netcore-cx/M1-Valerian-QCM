# -*- coding:utf-8 -*-
from flask import Flask, session, redirect, url_for, escape, request, render_template
import re
from lxml import etree
from os import listdir


#####=======================================================================================####
###   Return True si les varaibles de session username, formation, listmatiere sont définie  ###
def session_is_define():
    if 'username' in session and 'formation' in session and 'listmatiere' in session :
        return True
    else :
        return False


#####===================================================================####
###   Test si la chaine ne contient que des caractères de la whitelist   ###
def string_match(string, regexp = r'[A-Za-z0-9]'):
    return bool(re.compile(regexp).search(string))


#####===============================================================================#####
###   Test si l'utilisateur donné existe dans la base de permission xml               ###
###   Retourne une liste ["nom","formation","grade",["matiere1","matiere2"...,"matieren"] ]   ###
def request_session(username):
    tree = etree.parse("xml/perm.xml")

    xurl = "/utilisateurs/util[nom='" + username + "']/nom"
    user_request = tree.xpath(xurl)
    if not tree.xpath(xurl) :
        return False

    xurl = "/utilisateurs/util[nom='" + username + "']/formation"
    formation_request = tree.xpath(xurl)

    xurl = "/utilisateurs/util[nom='" + username + "']/grade"
    grade_request = tree.xpath(xurl)

    xurl = "/utilisateurs/util[nom='" + username + "']/listmatiere/matiere"
    listmatiere_request = tree.xpath(xurl)

    listmatiere_string = []
    for matiere in listmatiere_request:
        listmatiere_string.append(matiere.text)

    return [user_request[0].text, formation_request[0].text, grade_request[0].text, listmatiere_string]


#####==================================================================================================#####
###   Retourne une liste des fichiers du le dossier path et dont les fichers correspondent à la regexp   ###
###   list = ["qcm-1","qcm-2","qcm-3","qcm-n"]
def list_dir(path, regexp):
    list = []
    print(listdir(path))
    for file in listdir(path):
        if string_match(file, regexp) == True :
            list.append(file)
    return list

def list_xml_info(path, list_xml, formation, listmatiere) :
    list_qcm_info = []

    for xml in list_xml :
        xurl = path + xml
        tree = etree.parse(xurl)
        info = [ xml, tree.xpath("/QCM/formation")[0].text, tree.xpath("/QCM/matiere")[0].text, tree.xpath("/QCM/auteur")[0].text ]
        list_qcm_info.append(info)

    return list_qcm_info

def xml_allow_etudiant(path, xml, formation, listmatiere) :
    xurl = path + xml
    tree = etree.parse(xurl)
    if formation in tree.xpath("/QCM/formation")[0].text and tree.xpath("/QCM/matiere")[0].text in listmatiere :
        return True
    else :
        return False


def xml_allow_professeur(path, xml, auteur, listmatiere) :
    xurl = path + xml
    tree = etree.parse(xurl)
    if tree.xpath("/QCM/auteur")[0].text in auteur and tree.xpath("/QCM/matiere")[0].text in listmatiere :
        return True
    else :
        return False

#####=========================================================================================================================#####
###   Retourne une liste des fichiers dont l'utilisateur peut utiliser, critère en fonction de la formation et de la matiere   ###
def list_xml_allow(path, list_xml, formation, listmatiere, grade, nom) :

    list_qcm_allow = []
    for xml in list_xml:
        if grade == "etudiant" :
            if xml_allow_etudiant(path, xml, formation, listmatiere) == True :
                list_qcm_allow.append(xml)
        elif grade == "professeur" :
            if xml_allow_professeur(path, xml, nom, listmatiere) :
                list_qcm_allow.append(xml)

    return list_qcm_allow