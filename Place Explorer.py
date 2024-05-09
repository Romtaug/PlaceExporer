# Ajoutez météo et la température juillet, aout

import requests
import time
from prettytable import PrettyTable
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import sys
import os

###########################################################################################################################
#Places 
def get_place_details(place_id, api_key):
    details_url = "https://maps.googleapis.com/maps/api/place/details/json"
    details_params = {
        'place_id': place_id,
        'fields': 'name,formatted_address,rating,user_ratings_total,price_level,international_phone_number,website',
        'key': api_key
    }
    response = requests.get(details_url, params=details_params)
    if response.status_code == 200:
        return response.json().get('result', {})
    else:
        print(f"Failed to fetch details for place_id: {place_id}")
        return None

def search_places(api_key, location, category, max_results=10):
    url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
    params = {
        'query': f'{category} in ' + location,
        'key': api_key
    }
    
    places = []
    while True:
        response = requests.get(url, params=params)
        if response.status_code == 200:
            results = response.json()
            places.extend(results['results'])
            
            if 'next_page_token' not in results:
                break
            
            params['pagetoken'] = results['next_page_token']
            time.sleep(2)  # Google requires a short delay before requesting the next page
        else:
            print("Failed to fetch data from Google Places API")
            break

    detailed_places = []
    for place in places:
        details = get_place_details(place['place_id'], api_key)
        if details:
            detailed_places.append({
                'name': details.get('name', '?'),
                'address': details.get('formatted_address', '?'),
                'rating': details.get('rating', '?'),
                'total_reviews': details.get('user_ratings_total', 0),
                'price_level': details.get('price_level', '?'),
                'phone': details.get('international_phone_number', '?'),
            })

    # Sort places by the number of reviews
    detailed_places.sort(key=lambda x: x['total_reviews'], reverse=True)

    # Display the sorted results
    table = PrettyTable()
    table.field_names = ["Name", "Address", "Rating", "Total Reviews", "Price Level", "Phone"]

    for place in detailed_places[:max_results]:
        table.add_row([
            place['name'],
            place['address'],
            place['rating'],
            place['total_reviews'],
            place['price_level'],
            place['phone']
        ])
    
    #print(f"\nTop {max_results} Most Reviewed {category.capitalize()} in {location}:\n")
    return(table)

#####################################################################################################################
# eat/drink : # restaurants # cafes # bars # bakeries
# sleep : hotels # motels # inns # bed_and_breakfasts
# visit inside : # museums # art_galleries # places_of_worship # libraries # historical_sites
# visit outside : # parks # botanical_gardens # zoos # beaches # nature_reserves # monuments # beaches # mountains
# buy : # shopping_malls # boutiques # markets # supermarkets # bookstores # pet_stores
# events : # movie_theaters # theaters # operas # concert_halls # music_venues # festivals
# sport : # gyms # yoga_studios # sports_centers # spas # bowling_alleys # golf_courses
# hospitals : # clinics # dentists # pharmacies # veterinarians # medical_labs
# student : # schools # colleges # universities # laundries # libraries # tutoring_centers
# emergency : # banks # atms # police_stations # fire_stations # hospitals # urgent_care_centers
# administrative : # post_offices # city_halls # courthouses # embassies # government_offices # community_centers
# car : gas_stations # auto_repair_shops # parking_lots # car_wash # car_rentals
api_key = 'AIzaSyAyUJjhcjpgG9MIZceqkfjnznN00SYi9gQ'
location='Paris, France'
max_results=5
print("-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------")

print("\n\nEating/Drinking:")
print(search_places(api_key, location, 'restaurants', max_results))
search_places(api_key, location, 'bars', max_results)
#search_places(api_key, location, 'cafes', max_results=10)
"""
print("\n\nVisiting :")
search_places(api_key, location, 'historical_sites', max_results)
search_places(api_key, location, 'parks', max_results)
search_places(api_key, location, 'museums', max_results)
#search_places(api_key, location, 'art_galleries', max_results=10)
#search_places(api_key, location, 'botanical_gardens', max_results=10)      
#search_places(api_key, location, 'monuments', max_results=10)

print("\n\nPartying:")
search_places(api_key, location, 'movie_theaters', max_results)
search_places(api_key, location, 'concert_halls', max_results)
search_places(api_key, location, 'nightclubs', max_results)
print("-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------")

print("\n\nBuying:")
search_places(api_key, location, 'boutiques', max_results)
search_places(api_key, location, 'markets', max_results)
search_places(api_key, location, 'supermarkets', max_results)
print("-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------")


print("\n\nOther entertainment:")
search_places(api_key, location, 'amusement parks', max_results)
search_places(api_key, location, 'zoos', max_results)
search_places(api_key, location, 'aquariums', max_results)
print("-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------")


print("\n\nOther activities:")
search_places(api_key, location, 'campgrounds', max_results)
search_places(api_key, location, 'hiking trails', max_results)
search_places(api_key, location, 'beaches', max_results)
search_places(api_key, location, 'ski resorts', max_results)
search_places(api_key, location, 'sports_centers', max_results)
"""

###############################################################################################################################
#Meteo 
def get_current_weather(api_key, location):
    """Obtient les conditions météorologiques actuelles pour une ville donnée et recommande quoi emporter en fonction de la température."""
    url = f"http://api.openweathermap.org/data/2.5/weather?q={location}&appid={api_key}&units=metric"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        temperature = data['main']['temp']
        advice = ""

        if temperature <= 5:
            advice = "Il fait très froid! Assurez-vous d'emporter des vêtements chauds, comme un manteau épais, des gants et un bonnet. "
        elif temperature <= 15:
            advice = "Il fait un peu frais. Pensez à prendre un pull ou une veste, et peut-être un chapeau léger. "
        elif temperature <= 25:
            advice = "La température est agréable. Un t-shirt ou une chemise à manches longues devrait suffire. "
        else:
            advice = "Il fait chaud! Prévoyez des vêtements légers comme des shorts et des t-shirts."

        return f"La température actuelle à {location} est de {temperature}°C. {advice}"
    else:
        return "Erreur lors de la récupération des données météorologiques: " + response.text

###############################################################################################################################
    
def get_access_token(client_id, client_secret):
    response = requests.post("https://test.api.amadeus.com/v1/security/oauth2/token", data={
        'client_id': client_id,
        'client_secret': client_secret,
        'grant_type': 'client_credentials'
    })
    return response.json().get('access_token') if response.status_code == 200 else None

def search_cheapest_flight(access_token, origin, destination, date, adults, children):
    response = requests.get("https://test.api.amadeus.com/v2/shopping/flight-offers", headers={
        'Authorization': f'Bearer {access_token}'
    }, params={
        'originLocationCode': origin,
        'destinationLocationCode': destination,
        'departureDate': date,
        'adults': adults,
        'children': children,
        'max': 1
    })
    if response.status_code == 200 and response.json()['data']:
        flight = response.json()['data'][0]
        # Vous pouvez remplacer ce lien par un lien direct vers le site de réservation spécifique si vous avez cette information
        booking_link = f"https://www.google.com/flights?hl=fr#flt={origin}.{destination}.{date};c:EUR;e:1;px:2;a:;sd:1;t:f;tt:o"
        return f"Le vol le moins cher trouvable le {date} de {flight['itineraries'][0]['segments'][0]['departure']['iataCode']} à {flight['itineraries'][0]['segments'][-1]['arrival']['iataCode']} coûte {flight['price']['total']} euros. Pour réserver, visitez: {booking_link}"
    return "Aucun vol trouvé."


###############################################################################################################################

def prepare_email_body(api_key, location, category, max_results=5):
    table = search_places(api_key, location, category, max_results)
    # Convertit la PrettyTable en chaîne de caractères pour le corps de l'e-mail
    return table.get_string()

def to_send(api_key, location, max_results=5):
    # Initialisation du contenu de l'email avec une touche accueillante et enthousiaste
    email_content = f"🌟✈️ Bienvenue à bord de Place Explorer ! ✈️🌟\nPréparez-vous à découvrir les merveilles de {location}, une destination rêvée pour des aventures inoubliables. Voici un guide exclusif des meilleures attractions pour rendre votre séjour magique et mémorable (si les tableaux sont erronés n'hesitez pas à consulter le fichier 'PlaceExplorer.txt'ci-joint :\n\n"
    email_content += get_current_weather(api_key2, location)
    email_content += search_cheapest_flight(get_access_token(api_key3, api_secret3), origin, destination, date, 1, 0)
    email_content += "\n\n"
    # Les catégories suivantes utilisent la même structure : ajout de la description avec émojis et appel à prepare_email_body pour générer le contenu
    
    categories = {
        'historical_sites': '🏛️ Plongez dans l\'histoire avec ces sites historiques captivants, témoins du passé glorieux de {location} :\n',
        'parks': '🌳 Respirez l\'air frais dans les plus beaux parcs, idéaux pour une pause nature en plein cœur de la ville :\n',
        'museums': '🖼️ Cultivez votre esprit en visitant ces musées fascinants, où art et culture se rencontrent :\n',
        'restaurants': '🍴 Dégustez les délices culinaires dans les meilleurs restaurants que {location} a à offrir :\n',
        'bars': '🍹 Vibrez au rythme de la nuit dans nos bars recommandés, parfaits pour des soirées animées :\n',
        'movie_theaters': '🎬 Profitez d\'une soirée cinéma dans des salles sélectionnées pour leur confort et qualité:\n',
        'concert_halls': '🎶 Vivez des moments mémorables lors de concerts inoubliables dans nos salles recommandées :\n',
        'nightclubs': '💃 Dansez jusqu\'au bout de la nuit dans les boîtes de nuit les plus en vogue de {location} :\n',
        'boutiques': '🛍️ Faites du shopping dans les boutiques les plus chics pour des trouvailles uniques et tendance :\n',
        'markets': '🌽 Explorez les marchés locaux pour une expérience authentique et des produits frais :\n',
        'supermarkets': '🛒 Visitez les supermarchés pour tous vos besoins quotidiens, sélectionnés pour leur qualité et service :\n',
        'amusement_parks': '🎢 Découvrez le frisson dans nos parcs d\'attractions, parfaits pour une journée d\'aventures excitantes :\n',
        'zoos': '🐘 Rencontrez des animaux exotiques dans les zoos les plus respectés de {location} :\n',
        'aquariums': '🐠 Plongez dans le monde sous-marin avec une visite dans les meilleurs aquariums :\n',
        'campgrounds': '🏕️ Connectez-vous avec la nature et relaxez-vous dans les meilleurs terrains de camping :\n',
        'hiking_trails': '🥾 Parcourez les sentiers de randonnée pour une expérience revigorante en plein air :\n',
        'beaches': '🏖️ Profitez du soleil et du sable sur les plus belles plages :\n',
        'ski_resorts': '⛷️ Glissez sur les pistes dans les meilleures stations de ski de {location} :\n',
        'sports_centers': '🏋️‍♂️ Restez actif dans les centres sportifs offrant les meilleures installations et équipements :\n',
        'spas': '💆‍♀️ Détendez-vous et revitalisez-vous dans les spas les plus luxueux :\n'
    }

    # Générer la section pour chaque catégorie
    count = 20
    for key, intro in categories.items():
        email_content += intro
        email_content += prepare_email_body(api_key, location, key, max_results) + "\n\n"
        print(count)  # Afficher le compteur
        count -= 1  # Décrémenter le compteur

    
    # Ajout de l'incitation à planifier avec My Maps
    email_content += "🗺️ Planifiez votre aventure parfaite avec My Maps pour une expérience personnalisée et sans tracas ! Commencez ici : https://www.google.com/mymaps\n\n"
    email_content += "Nous espérons que vous trouverez ces recommandations utiles pour un voyage mémorable. Bon voyage ! 🌍✨ N'hésitez pas à faire un don PayPal à l'adresse romtaug@gmail.com."
    
    return email_content.format(location=location)

##############################################################################################################################
# APIs
api_key = 'AIzaSyAyUJjhcjpgG9MIZceqkfjnznN00SYi9gQ'  # API Events
api_key2 = 'de1470253d46ffd4259f9cfd0d430cea'  # API Meteo
# API vols
api_key3 = 'ojkwuc6SaBcIziwDlxNbv6xmMYGxsA9a'
api_secret3 = 'oRaoDqd4bwOAksPs'
#############################################################################################################################
# Vol
origin = 'CDG'
destination = 'JFK'
date = '2024-08-01'

# Location
print("Please enter the location (city, country):")
location = input()
print("")

# Nombre de lignes
max_results=5

#Vérification des APIs
print("Vérification des APIs :\n")
print(search_places(api_key, location, 'restaurants', max_results))
print(get_current_weather(api_key2, location))
print(search_cheapest_flight(get_access_token(api_key3, api_secret3), origin, destination, date, 1, 0))

print("\n\nVoici le message a envoyer (soyez patient le programme peut mettre du temps à s'exécuter) :\n")
email_body = to_send(api_key, location, max_results)
print(email_body)
print("\n")

####################################################################################################################
#Email
# N'oubliez pas d'activer le mot de passe pour les applications externes dans les paramètres de votre compte Gmail
smtp_server = "smtp.gmail.com"
port = 465  # SSL
sender_email = "taugourdea@cy-tech.fr"
password = "" # De votre email
receiver_email = ""
server = smtplib.SMTP_SSL(smtp_server, port)
server.login(sender_email, password)

# Création de l'objet MIMEMultipart pour le message
msg = MIMEMultipart()
msg['From'] = sender_email
msg['To'] = receiver_email
msg['Subject'] = f"Informations sur les lieux à {location} - Place Explorer"
from email.mime.image import MIMEImage

# Chemins vers les images que vous souhaitez joindre
image_paths = ["image/logo.png", "image/travel.png", "image/qrcode.png"]

# Liste pour stocker les objets MIMEImage
images = []

# Boucle pour lire et créer les objets MIMEImage pour chaque image
for image_path in image_paths:
    with open(image_path, 'rb') as image_file:
        image_data = image_file.read()
    image = MIMEImage(image_data)
    image.add_header('Content-Disposition', 'attachment', filename=image_path.split('/')[-1])
    images.append(image)

# Ajout des images à votre message
for image in images:
    msg.attach(image)

# Préparation du corps de l'e-mail
body = email_body
#print(prepare_email_body(api_key, location, 'restaurants', max_results))
msg.attach(MIMEText(body, 'plain', 'utf-8'))  # Spécification de l'encodage UTF-8

######################################################################################################
def save_to_directory(content, filename):
    # Utiliser un chemin relatif pour sauvegarder le fichier dans le même dossier que le script
    # '__file__' est une variable spéciale utilisée pour obtenir le chemin du script courant
    directory_path = os.path.dirname(os.path.abspath(__file__))

    full_path = os.path.join(directory_path, filename)

    # Écrire le contenu dans le fichier
    try:
        with open(full_path, 'w', encoding='utf-8') as file:
            file.write(content)
            print(f"Le contenu a été enregistré dans {full_path}")
    except Exception as e:
        print(f"Erreur lors de l'écriture dans le fichier : {e}")

def attach_file_to_email(msg, file_path):
    """
    Attache un fichier au message MIME.
    """
    # Créer un objet MIMEBase et lui attacher le fichier
    part = MIMEBase('application', "octet-stream")
    with open(file_path, 'rb') as file:
        part.set_payload(file.read())
    encoders.encode_base64(part)
    part.add_header('Content-Disposition', 'attachment; filename="{}"'.format(os.path.basename(file_path)))
    msg.attach(part)

# Nom du fichier à sauvegarder et chemin
filename = "PlaceExplorer.txt"
file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)
save_to_directory(email_body, filename)

# Attacher le fichier
attach_file_to_email(msg, file_path)

##################################################################################################
# Envoi de l'e-mail
print("\nEnvoi de l'email...")# Envoi de l'e-mail
server.send_message(msg)
print(f"Email sent successfully to {receiver_email} for the location {location}!")

# Fermeture de la connexion
server.quit()
