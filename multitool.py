import os
import requests
import json
import re
import hashlib
from datetime import datetime
from bs4 import BeautifulSoup

if not os.path.exists("Account"):
    os.mkdir("Account")

CREDIT = "Tool créé par DataLee404 - 2025 - NextGen OSINT"

def save_result_txt(name, content):
    filename = f"Account/{name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(f"{CREDIT}\n\n")
        f.write(content)
    print(f"[+] Résultat sauvegardé dans {filename}")

def lookup_instagram_advanced(username):
    print(f"[Instagram Advanced] @{username}")
    url = f"https://www.instagram.com/{username}/"
    headers = {"User-Agent":"Mozilla/5.0"}
    try:
        res = requests.get(url, headers=headers)
        if res.status_code != 200:
            print("Profil introuvable ou privé")
            return
        soup = BeautifulSoup(res.text, 'html.parser')
        scripts = soup.find_all("script", type="text/javascript")
        shared_data = None
        for script in scripts:
            if script.string and 'window._sharedData =' in script.string:
                shared_data = script.string
                break
        if not shared_data:
            print("Données non trouvées")
            return
        json_text = shared_data.strip().replace("window._sharedData = ", "")[:-1]
        data = json.loads(json_text)
        user = data['entry_data']['ProfilePage'][0]['graphql']['user']
        bio = user.get('biography', '')
        hashtags = re.findall(r"#(\w+)", bio)
        posts = user['edge_owner_to_timeline_media']['edges'][:5]
        post_captions = []
        for post in posts:
            node = post['node']
            caption_edges = node['edge_media_to_caption']['edges']
            caption_text = caption_edges[0]['node']['text'] if caption_edges else ''
            post_captions.append(caption_text)
        is_influencer = (user['edge_followed_by']['count'] > 100000 and len(bio) > 100)
        content = (
            f"Instagram Lookup avancé : @{username}\n"
            f"Nom complet: {user.get('full_name','N/A')}\n"
            f"Bio: {bio}\n"
            f"Hashtags bio: {hashtags}\n"
            f"Followers: {user['edge_followed_by']['count']}\n"
            f"Following: {user['edge_follow']['count']}\n"
            f"Posts totaux: {user['edge_owner_to_timeline_media']['count']}\n"
            f"Profil privé: {user['is_private']}\n"
            f"Profil vérifié: {user['is_verified']}\n"
            f"Influenceur probable: {is_influencer}\n"
            f"\n5 derniers posts (captions):\n"
        )
        for i, caption in enumerate(post_captions, 1):
            content += f"{i}. {caption}\n"
        save_result_txt(f"insta_advanced_{username}", content)
    except Exception as e:
        print(f"Erreur Instagram Advanced: {e}")

def lookup_tiktok_trending(username):
    print(f"[TikTok Trending] @{username}")
    url = f"https://www.tiktok.com/@{username}"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        res = requests.get(url, headers=headers)
        if res.status_code != 200:
            print("Profil introuvable ou privé")
            return
        soup = BeautifulSoup(res.text, 'html.parser')
        json_ld = soup.find('script', type='application/ld+json')
        if not json_ld:
            print("Données JSON-LD non trouvées")
            return
        data = json.loads(json_ld.string)
        name = data.get('name', 'N/A')
        desc = data.get('description', 'N/A')
        video_count = data.get('interactionStatistic', {}).get('userInteractionCount', 'N/A')
        videos = []
        for video in soup.find_all('div', class_='tiktok-1soki6-DivVideoContainer')[:5]:
            video_link = video.find('a', href=True)
            if video_link:
                videos.append(video_link['href'])
        content = (
            f"TikTok Lookup avancé: @{username}\n"
            f"Nom: {name}\n"
            f"Description: {desc}\n"
            f"Interactions: {video_count}\n"
            f"5 dernières vidéos (URL partielles):\n"
        )
        for i, v in enumerate(videos, 1):
            content += f"{i}. {v}\n"
        save_result_txt(f"tiktok_{username}", content)
    except Exception as e:
        print(f"Erreur TikTok Lookup: {e}")

def lookup_email_reputation(email):
    print(f"[Email Reputation] {email}")
    try:
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            print("Email invalide")
            return
        gravatar_hash = hashlib.md5(email.lower().encode()).hexdigest()
        gravatar_url = f"https://www.gravatar.com/{gravatar_hash}.json"
        grav_res = requests.get(gravatar_url)
        gravatar_data = grav_res.json() if grav_res.status_code == 200 else None
        hibp_url = f"https://haveibeenpwned.com/unifiedsearch/{email}"
        hibp_res = requests.get(hibp_url, headers={"User-Agent": "Mozilla/5.0"})
        breach_status = "Possiblement exposé" if hibp_res.status_code == 200 else "Pas trouvé"
        content = (
            f"Email Reputation Lookup : {email}\n"
            f"Syntaxe : Valide\n"
            f"Gravatar profile : {'Trouvé' if gravatar_data else 'Non trouvé'}\n"
            f"Status breach HaveIBeenPwned : {breach_status}\n"
        )
        save_result_txt(f"email_reputation_{email.replace('@','_at_')}", content)
    except Exception as e:
        print(f"Erreur Email Reputation: {e}")

def lookup_tech_stack(url):
    print(f"[Tech Stack] {url}")
    try:
        res = requests.get(url)
        if res.status_code != 200:
            print("Site inaccessible")
            return
        html = res.text.lower()
        techs = []
        if "wordpress" in html:
            techs.append("WordPress")
        if "shopify" in html:
            techs.append("Shopify")
        if "jquery" in html:
            techs.append("jQuery")
        if "react" in html:
            techs.append("React")
        if "angular" in html:
            techs.append("Angular")
        if "php" in html:
            techs.append("PHP")
        if "python" in html:
            techs.append("Python")
        content = f"Tech Stack détectée sur {url} :\n" + ", ".join(techs) if techs else "Aucune technologie majeure détectée."
        save_result_txt(f"techstack_{url.replace('https://','').replace('http://','').replace('/','_')}", content)
    except Exception as e:
        print(f"Erreur Tech Stack Lookup: {e}")

def lookup_exif_image(image_url):
    print(f"[EXIF Image] {image_url}")
    try:
        res = requests.get(image_url)
        if res.status_code != 200:
            print("Image inaccessible")
            return
        from PIL import Image
        from io import BytesIO
        image = Image.open(BytesIO(res.content))
        exif_data = image._getexif()
        if not exif_data:
            print("Pas de données EXIF trouvées")
            return
        exif_str = ""
        for tag_id, value in exif_data.items():
            exif_str += f"{tag_id}: {value}\n"
        save_result_txt(f"exif_{image_url.split('/')[-1].split('?')[0]}", exif_str)
    except Exception as e:
        print(f"Erreur EXIF Image: {e}")

def lookup_geoip(ip):
    print(f"[GeoIP] {ip}")
    try:
        url = f"https://ipinfo.io/{ip}/json"
        res = requests.get(url)
        if res.status_code != 200:
            print("IP invalide ou inaccessible")
            return
        data = res.json()
        content = json.dumps(data, indent=2)
        save_result_txt(f"geoip_{ip.replace('.','_')}", content)
    except Exception as e:
        print(f"Erreur GeoIP: {e}")

def lookup_port_scan(ip):
    print(f"[Port Scan légal] {ip}")
    try:
        ports_to_scan = [80, 443, 22, 21, 25, 110, 143, 3306, 8080]
        import socket
        open_ports = []
        for port in ports_to_scan:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(0.5)
            result = sock.connect_ex((ip, port))
            if result == 0:
                open_ports.append(port)
            sock.close()
        content = f"Ports ouverts détectés sur {ip} : {open_ports if open_ports else 'Aucun'}"
        save_result_txt(f"portscan_{ip.replace('.','_')}", content)
    except Exception as e:
        print(f"Erreur Port Scan: {e}")

def lookup_blockchain_eth(address):
    print(f"[Blockchain ETH] {address}")
    try:
        url = f"https://api.blockcypher.com/v1/eth/main/addrs/{address}"
        res = requests.get(url)
        if res.status_code != 200:
            print("Adresse invalide ou inaccessible")
            return
        data = res.json()
        content = json.dumps(data, indent=2)
        save_result_txt(f"eth_{address}", content)
    except Exception as e:
        print(f"Erreur Blockchain ETH: {e}")

def lookup_instagram_hashtags_trending():
    print("[Instagram Hashtags Trending]")
    try:
        url = "https://www.instagram.com/explore/tags/"
        res = requests.get(url)
        if res.status_code != 200:
            print("Inaccessible")
            return
        content = "Fonctionnalité à implémenter (exemple placeholder)\n"
        save_result_txt("insta_hashtags_trending", content)
    except Exception as e:
        print(f"Erreur Hashtags Trending: {e}")

def lookup_github_secrets(username):
    print(f"[GitHub Secrets] {username}")
    try:
        url = f"https://api.github.com/users/{username}/repos"
        headers = {"Accept": "application/vnd.github.v3+json"}
        res = requests.get(url, headers=headers)
        if res.status_code != 200:
            print("Utilisateur GitHub invalide")
            return
        repos = res.json()
        leaks = []
        for repo in repos:
            repo_name = repo['name']
            url_contents = f"https://api.github.com/repos/{username}/{repo_name}/contents"
            c_res = requests.get(url_contents, headers=headers)
            if c_res.status_code != 200:
                continue
            files = c_res.json()
            for file in files:
                if file['name'].lower().endswith(('.env','.key','.pem','.config','.json','.yml','.yaml')):
                    leaks.append(file['name'] + " dans " + repo_name)
        content = "Fichiers sensibles potentiels trouvés:\n" + ("\n".join(leaks) if leaks else "Aucun fichier sensible détecté")
        save_result_txt(f"github_secrets_{username}", content)
    except Exception as e:
        print(f"Erreur GitHub Secrets: {e}")

def lookup_twitter_osint(username):
    print(f"[Twitter OSINT] {username}")
    try:
        url = f"https://twitter.com/{username}"
        headers = {"User-Agent": "Mozilla/5.0"}
        res = requests.get(url, headers=headers)
        if res.status_code != 200:
            print("Profil Twitter introuvable")
            return
        soup = BeautifulSoup(res.text, 'html.parser')
        name = soup.find("a", {"href": f"/{username}"}).text.strip() if soup.find("a", {"href": f"/{username}"}) else "N/A"
        tweets = soup.find_all("div", {"data-testid": "tweet"})
        tweets_texts = [tweet.get_text(separator=" ").strip()[:100] for tweet in tweets[:5]]
        content = f"Twitter OSINT : @{username}\nNom: {name}\n5 derniers tweets (extraits):\n"
        for i, t in enumerate(tweets_texts, 1):
            content += f"{i}. {t}\n"
        save_result_txt(f"twitter_osint_{username}", content)
    except Exception as e:
        print(f"Erreur Twitter OSINT: {e}")

def lookup_mastodon_public(username):
    print(f"[Mastodon Public] {username}")
    try:
        parts = username.split("@")
        if len(parts) != 2:
            print("Format Mastodon invalide (ex: user@instance.social)")
            return
        user, instance = parts
        url = f"https://{instance}/api/v1/accounts/lookup?acct={user}"
        res = requests.get(url)
        if res.status_code != 200:
            print("Utilisateur Mastodon introuvable")
            return
        data = res.json()
        content = json.dumps(data, indent=2)
        save_result_txt(f"mastodon_{username.replace('@','_')}", content)
    except Exception as e:
        print(f"Erreur Mastodon Lookup: {e}")

def lookup_domain_reputation(domain):
    print(f"[Domain Reputation] {domain}")
    try:
        url = f"https://api.abuseipdb.com/api/v2/check"
        headers = {
            'Accept': 'application/json',
            'Key': 'YOUR_ABUSEIPDB_API_KEY'
        }
        params = {'ipAddress': domain}
        res = requests.get(url, headers=headers, params=params)
        if res.status_code != 200:
            print("Requête API AbuseIPDB échouée (clé API requise)")
            return
        data = res.json()
        content = json.dumps(data, indent=2)
        save_result_txt(f"domain_reputation_{domain.replace('.','_')}", content)
    except Exception as e:
        print(f"Erreur Domain Reputation: {e}")

def lookup_phone_spam(phone):
    print(f"[Phone Spam Check] {phone}")
    try:
        url = f"https://api.stopscammer.io/phone/{phone}"
        res = requests.get(url)
        if res.status_code != 200:
            print("Numéro non trouvé dans la base StopScammer")
            return
        data = res.json()
        content = json.dumps(data, indent=2)
        save_result_txt(f"phone_spam_{phone}", content)
    except Exception as e:
        print(f"Erreur Phone Spam: {e}")

def lookup_phone_validation(phone):
    print(f"[Phone Validation] {phone}")
    try:
        url = f"https://numverify.com/api/validate?number={phone}&country_code=&format=1&access_key=YOUR_NUMVERIFY_API_KEY"
        res = requests.get(url)
        if res.status_code != 200:
            print("Requête API NumVerify échouée (clé API requise)")
            return
        data = res.json()
        content = json.dumps(data, indent=2)
        save_result_txt(f"phone_validation_{phone}", content)
    except Exception as e:
        print(f"Erreur Phone Validation: {e}")

def lookup_website_screenshot(url):
    print(f"[Website Screenshot] {url}")
    try:
        api_key = "YOUR_SCREENSHOT_API_KEY"
        api_url = f"https://api.screenshotapi.net/screenshot?token={api_key}&url={url}&output=image&file_type=png"
        # On télécharge l'image dans Account/
        res = requests.get(api_url)
        if res.status_code == 200:
            filename = f"Account/screenshot_{url.replace('https://','').replace('http://','').replace('/','_')}.png"
            with open(filename, "wb") as f:
                f.write(res.content)
            print(f"Screenshot sauvegardé : {filename}")
        else:
            print("Erreur API screenshot")
    except Exception as e:
        print(f"Erreur Screenshot Website: {e}")

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def menu():
    pages = {
        1: [lookup_instagram_advanced, lookup_tiktok_trending, lookup_email_reputation, lookup_tech_stack, lookup_exif_image],
        2: [lookup_geoip, lookup_port_scan, lookup_blockchain_eth, lookup_instagram_hashtags_trending, lookup_github_secrets],
        3: [lookup_twitter_osint, lookup_mastodon_public, lookup_domain_reputation, lookup_phone_spam, lookup_phone_validation],
        4: [lookup_website_screenshot],
        # 5 à 15 : placeholder, tu pourras ajouter d’autres fonctions dans la même logique
    }
    # Pour la démonstration, on duplique des fonctions pour 15 pages:
    for i in range(5,16):
        pages[i] = pages[1]  # Juste pour avoir 15 pages avec 5 fonctions

    while True:
        clear_screen()
        print(f"{CREDIT}\n\nMultitool OSINT 2025 - Sélectionnez une page (1-15) ou 0 pour quitter :")
        for p in range(1,16):
            print(f"Page {p} - 5 lookups")
        try:
            page = int(input("Page: "))
        except:
            continue
        if page == 0:
            print("Bye !")
            break
        if page not in pages:
            print("Page invalide")
            input("Appuyez sur Entrée...")
            continue
        funcs = pages[page]
        for i, func in enumerate(funcs, 1):
            print(f"{i}. {func.__name__.replace('lookup_','').replace('_',' ').capitalize()}")
        try:
            choice = int(input("Choisissez lookup (0 pour retour): "))
        except:
            continue
        if choice == 0:
            continue
        if not (1 <= choice <= len(funcs)):
            print("Choix invalide")
            input("Appuyez sur Entrée...")
            continue
        func = funcs[choice-1]
        clear_screen()
        param = input("Entrez paramètre (ex: username, email, ip, url...) : ").strip()
        func(param)
        input("Appuyez sur Entrée pour continuer...")

if __name__ == "__main__":
    menu()
