#!/usr/bin/env python3
import argparse
import ovh
import requests
import os
from dotenv import load_dotenv

# --- CHARGEMENT DES VARIABLES D'ENVIRONNEMENT ---

# 1. On récupère le chemin du dossier utilisateur (ex: /home/utilisateur)
user_home = os.path.expanduser("~")

# 2. On cible le fichier spécifique .ovh-sub.env
env_filename = ".env"
env_directory = ".ovh-sub"
env_path = os.path.join(user_home, env_directory, env_filename)

# 3. Vérification et chargement
if not os.path.exists(env_path):
    print(f"❌ Erreur de configuration.")
    print(f"Le fichier de clés est introuvable ici : {env_path}")
    print(f"Veuillez créer ce fichier avec vos clés OVH (OVH_APP_KEY, etc.)")
    sys.exit(1)

load_dotenv(env_path)

# 4. Récupération sécurisée des variables
try:
    ENDPOINT = os.getenv('OVH_ENDPOINT', 'ovh-eu')
    APP_KEY = os.getenv('OVH_APP_KEY')
    APP_SECRET = os.getenv('OVH_APP_SECRET')
    CONSUMER_KEY = os.getenv('OVH_CONSUMER_KEY')

    if not all([APP_KEY, APP_SECRET, CONSUMER_KEY]):
        raise ValueError(f"Variables manquantes dans {env_path}")

    OVH_CLIENT = ovh.Client(
        endpoint=ENDPOINT,
        application_key=APP_KEY,
        application_secret=APP_SECRET,
        consumer_key=CONSUMER_KEY,
    )
except Exception as e:
    print(f"❌ Erreur de lecture des variables : {e}")
    sys.exit(1)

# ---------------------


def get_public_ip():
    print("🔍 Récupération de votre IP publique...")
    try:
        ip = requests.get('https://api.ipify.org', timeout=5).text
        print(f"✅ IP trouvée : {ip}")
        return ip
    except requests.RequestException as e:
        print(f"❌ Erreur lors de la récupération de l'IP : {e}")
        sys.exit(1)
        
        
def get_domain_record_id(domain, subdomain, delete_sub=False):
    full_domain = f"{subdomain}.{domain}"
    
    try:
        print(f"⚙️  Vérification de {full_domain} sur la zone {domain}...")
        
        records = OVH_CLIENT.get(
            f'/domain/zone/{domain}/record', 
            fieldType='A', 
            subDomain=subdomain
        )
        
        if records and not delete_sub:
            record_id = records[0]
            print(f"⚠️  Le sous-domaine existe déjà (ID: {record_id}).")
            
            return record_id
        elif records and delete_sub:
            record_id = records[0]
            print(f"⚠️  Le sous-domaine existe (ID: {record_id}).")
            
            return record_id
        elif not records and delete_sub:
            return 0
        else:
            print(f"✅  Le sous-domaine n'existe pas.")
            
            return 0
    except ovh.exceptions.APIError as e:
        print(f"❌ Erreur API OVH : {e}")

def display_message(domain, subdomain, base_message, dry_run=False):
    full_domain = f"{subdomain}.{domain}"
    
    dry_run_message = "[DRY RUN] - " if dry_run else ""
    
    message = f"{dry_run_message}{base_message} : {full_domain}"
    print(message)

def create(domain, subdomain, target_ip, dry_run=False):
    base_message = f"🔄 Création sous-domaine"
    display_message(domain, subdomain, base_message, dry_run)
    
    if not dry_run:
        OVH_CLIENT.post(
            f'/domain/zone/{domain}/record', 
            fieldType='A', 
            subDomain=subdomain, 
            target=target_ip,
            ttl=60) 

def delete(domain, subdomain, record_id, dry_run=False):
    base_message = f"🔄 Suppréssion sous-domaine"
    display_message(domain, subdomain, base_message, dry_run)
    
    if not dry_run:
        OVH_CLIENT.delete(f'/domain/zone/{domain}/record/{record_id}')
    
def update(domain, subdomain, record_id, target_ip, dry_run=False):
    base_message = f"🔄 Mise à jour sous-domaine"
    display_message(domain, subdomain, base_message, dry_run)
    
    if not dry_run:
        OVH_CLIENT.put(f'/domain/zone/{domain}/record/{record_id}', target=target_ip)

def refresh_dns(domain, subdomain, dry_run=False):
    base_message = f"🔄 Application des changements (Refresh Zone)..."
    display_message(domain, subdomain, base_message, dry_run)
    
    if not dry_run:
        OVH_CLIENT.post(f'/domain/zone/{domain}/refresh')

def main(domain, subdomain, dry_run=False, remove_sub=False, force=False):    
    target_ip = get_public_ip()
    full_domain = f"{subdomain}.{domain}"
    
    try:
        record_id = get_domain_record_id(domain, subdomain, remove_sub)
        
        # Si le sous-domain existe
        if record_id != 0:
            if remove_sub:
                # delete an existing sub domain
                if force:
                    print(f"Delete an existing sub domain")   
                    delete(domain, subdomain, record_id, dry_run) 
                else:
                    choice = input(f"Êtes-vous sur de vouloir supprimer le sous-domaine ({subdomain}) ? (o/n) : ")
                    
                    if choice.lower() == 'o':
                        delete(domain, subdomain, record_id, dry_run)
                        print("✅ Suppréssion effectuée.")
                    else:
                        print("❌ Opération annulée.")
                        return
            else:
                update(domain, subdomain, record_id, target_ip, dry_run)
        else:
            if remove_sub:
                print(f"❌ Le sous-domaine n'existe pas.")
            else:
                create(domain, subdomain, target_ip, dry_run)
        
        refresh_dns(domain, subdomain, dry_run)
    except ovh.exceptions.APIError as e:
        print(f"❌ Erreur API OVH : {e}")
    
if __name__ == "__main__":    
    parser = argparse.ArgumentParser(description="Outil CLI OVH")
    
    # Argument Positionnel (Obligatoire)
    parser.add_argument("domain", help="Nom de domaine de base (ex : mondomaine.fr)")
    parser.add_argument("subdomain", help="Nom du sous-domaine (ex : vpn)")
    
    # Arguments Optionnels
    parser.add_argument("-d", "--dry", action="store_true", help="Lance la commande en mode dry run.")
    parser.add_argument("-r", "--remove", action="store_true", help="Supprime le sous-domaine.")
    parser.add_argument("-f", "--force", action="store_true", help="Ne demande pas de confirmation.")
    
    args = parser.parse_args()
    
    main(args.domain, args.subdomain, dry_run=args.dry, remove_sub=args.remove, force=args.force)