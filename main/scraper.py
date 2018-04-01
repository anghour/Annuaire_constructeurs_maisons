__author__= "Azziz ANGHOUR, TONTON_GROUP"
__email__= "anghour@gmail.com"
__version__= "1.0.0"

import time

from bs4 import BeautifulSoup
from selenium import webdriver

from models.constructor_model import *


#--------------------------------------------------------#
#------------------------ Fonctions ---------------------#
#--------------------------------------------------------#


def get_browser():

    """
    :return: cette fonction démarre le navigateur (FireFox) et renvoie sa référence

    """
    profile = webdriver.FirefoxProfile()
    profile.set_preference("general.useragent.override",
                           "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:57.0) Gecko/20100101 Firefox/57.0")
    return webdriver.Firefox(profile)

def get_html_content(browser, url):

    """
    :param browser: la référence vers le navigateur.
    :param url: la page web à charger.
    :return: cette fonction renvoie le contenu html de la page web dont l'adresse est envovée en paramètres (url)
            ou None si un problème est survenu.
    """
    print("PAGE LOADING => ", url)
    try:
        browser.get(url)
    except :
        print("ERREUR DE CHARGEMENT DE L'URL : ", url)
        return None

    time.sleep(3)
    htmlContent = browser.execute_script("return document.body.innerHTML")
    return BeautifulSoup(htmlContent, 'lxml')

def get_regions(browser, start_url):

    """

    :param browser: la référence vers le navigateur.
    :param start_url: l'url de départ.
    :return: cette fonction renvoie une liste d'objets "Region" représentant l'ensemble des régions de la France.
            Une Region est décrite par son nom et le lien menant vers sa liste de départements.
    """

    html_content = get_html_content(browser, start_url) # chargement de la page

    if (html_content == None):# en cas de problème la fonction renvoie None
        return None
    try:
        regions_list = []
        regions_ul = html_content.find(id='links')
        for a in regions_ul.find_all(class_='link-region'):
            name = a.span.text.strip()
            link = a['href']
            regions_list.append(Region(name, link))
        return regions_list

    except:
        print('ERROR REGION PAGE')
        return None


def get_departements(browser, region):

    """
    :param browser: la référence vers le navigateur.
    :param region: la référence vers la région (objet Region) dont on cherche à récupérer la liste de départements.
    :return: cette fonction renvoie l'ensemble de départements de la région envoyée en paramètres (region)
            ou None en cas de problème. Un département (objet Departement) est décrite par son nom (attribut 'name')
            et le lien (attribut 'link') menant vers sa liste de constructeurs de maisons individuelles.
    """
    base_url = 'http://www.batisseur.fr'
    dept_url = base_url + region.link

    html_content = get_html_content(browser, dept_url)
    if (html_content == None):
        return None
    try:
        dept_list = []
        dept_ul = html_content.find(id='links')
        for a in dept_ul.find_all(class_='link-dept'):
            name = a.span.text.strip()
            link = a['href']
            dept_list.append(Departement(name, link))
        return dept_list
    except:
        print('ERROR DEPT PAGE !.')
        return None


def get_constructors(browser, dept):

    """

    :param browser: la référence vers le navigateur.
    :param dept: la référence vers le département (objet de la classe Departement) dont on cherche à récupérer
                l'ensemble de constructeurs.
    :return: cette fonction renvoie la liste de constructeurs du département en question ou None en cas
            de problème. Un constructeur est représenté par son intitulé, le code de son département, son adresse,
            son numéro de téléphone et le lien de son site web.
    """


    base_url = 'http://www.batisseur.fr'
    constructors_url = base_url + dept.link

    html_content = get_html_content(browser, constructors_url)
    if (html_content == None):
        return None

    try:
        constructors_list = []

        constr_ul = html_content.find(id='links')

        # Extraction du code de département en question
        dept_code = html_content.find(id='content').find('h3').text.split('(')[1].split(')')[0]

        # les constructeurs d'un département peuvent être affichés sur une ou plusieurs pages.
        # cela dépend du nombre de constructeurs présents dans le département
        pages = html_content.find(id='pages')

        pages_number = 1 # nombre de pages par défaut est égale à 1
        if(pages != None): # dans le cas où les constructeurs sont affichés sur plusieurs pages (pagination)
            pages_number = len(pages.find_all('a'))

        for i in range(1, pages_number):
            if(i > 1): # si plusieurs pages
                current_url = constructors_url + '?p='+str(i) # ajout du numéro de la page dans l'url
                html_content = get_html_content(browser, current_url) # chargement de la page
                constr_ul = html_content.find(id='links') # la liste des constructeurs (<ul>)

            for li_item in constr_ul.find_all(class_='link-item '): # pour chaque <li> de <lu>
                constructor_link = li_item.a['href'] # site web du constructeur
                constructor_intitule = li_item.a.text.split('\n')[1].strip() # intitulé du constructeur (son nom)
                spans = li_item.a.find_all('span')
                constructor_address = spans[1].text.strip() # adresse du constructeur

                # numéro de téléphone en supprimant les séparateurs entre les chiffres (espace ou point)
                constructor_tel = spans[2].text.split(':')[1].replace(' ', '').replace('.', '')

                # création d'un objet Constructor
                constructor = Constructor(intitule=constructor_intitule,
                                          dept_code=dept_code,
                                          address=constructor_address,
                                          link=constructor_link,
                                          phone=constructor_tel)
                # ajout du constructeur dans la liste
                constructors_list.append(constructor)
        return constructors_list

    except:
        print('ERROR CONSTRUCTORS PAGE => ', dept.name)
        return None


def get_annuaire(url):

    """

    :param url: l'url de départ.
    :return: cette fonction fait appel aux méthodes précedentes pour construire l'annuaire
            de constructeurs de maisons individuelles. Elle renvoie l'annuaire construit
            ou None en cas de problème.
    """


    browser = get_browser() # récupération du navigateur
    regions = get_regions(browser, start_url=url) # récupération des régions
    if(regions != None):
        annuaire = Annuaire() # initialisation d'un objet Annuaire
        for region in regions: # pour chaque région, récupérer la liste de départements
            depts = get_departements(browser, region)
            if(depts != None):
                for dept in depts: # pour chaque département, récupérer la liste de constructeurs
                    constrs = get_constructors(browser, dept)
                    if(constrs != None):
                        for ele in constrs: # pour chaque constructeur, créér l'objet Annuaire_Item correspondant
                            intitule = ele.intitule
                            dept_code = ele.dept_code
                            address = ele.address
                            phone = ele.phone
                            website = ele.link

                            # création de l'objet Annuaire_Item
                            item = Annuaire_Item(intitule=intitule,
                                                 region= region.name,
                                                 departement=dept.name,
                                                 dept_code=dept_code,
                                                 address=address,
                                                 phone=phone,
                                                 website=website)
                            annuaire.add_constructor(item=item) # ajout de l'item dans l'annuaire

        return annuaire
    return None

def csv_annuaire_save(annuaire):

    """
    :param annuaire: l'annuaire de constructeurs
    :return: cette fonction permet d'enregistrer l'annuaire de constructeurs dans un fichier CSV

    """

    csv_document = open('../data/constructors_annuaire.csv','a')
    header = "intitule;region;departement;departement_code;address;phone;website"
    csv_document.write(header)
    for item in annuaire.constructor_list:
        row = '\n'+item.intitule + ';' + item.region + ';' + item.departement \
            + ';' + item.departement_code + ';' + item.address \
            + ';' + item.phone + ';' + item.website
        csv_document.write(row)
    csv_document.close()

#--------------------------------------------------------------------------------#
#----------------------------- PROGRAMME PRINCIPAL ------------------------------#
#--------------------------------------------------------------------------------#


base_url = 'http://www.batisseur.fr'
start_url = base_url+'/annuaire-constructeur-maison.html'
annuaire = get_annuaire(url=start_url) # remplissage de l'annuaire
csv_annuaire_save(annuaire=annuaire) # enregistremment de l'annuaire
