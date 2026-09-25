#!/usr/bin/env python3
import argparse
import ipaddress
import sys
import ovh
import requests
import os
from dotenv import load_dotenv

def load_ovh_client(profile='default'):
    user_home = os.path.expanduser("~")
    env_directory = ".ovh-sub"
    env_path = os.path.join(user_home, env_directory, f"{profile}.env")

    # Rétrocompatibilité : si profil "default" et fichier ancien format (.env)
    if not os.path.exists(env_path) and profile == 'default':
        legacy_path = os.path.join(user_home, env_directory, ".env")
        if os.path.exists(legacy_path):
            env_path = legacy_path

    if not os.path.exists(env_path):
        print(f"❌ Erreur de configuration.")
        print(f"Le fichier de clés est introuvable ici : {env_path}")
        print(f"Créez-le avec : ./setup.sh -n {profile} -k <APP_KEY> -s <APP_SECRET> -c <CONSUMER_KEY>")
        sys.exit(1)

    load_dotenv(env_path)

    try:
        endpoint = os.getenv('OVH_ENDPOINT', 'ovh-eu')
        app_key = os.getenv('OVH_APP_KEY')
        app_secret = os.getenv('OVH_APP_SECRET')
        consumer_key = os.getenv('OVH_CONSUMER_KEY')

        if not all([app_key, app_secret, consumer_key]):
            raise ValueError(f"Variables manquantes dans {env_path}")

        return ovh.Client(
            endpoint=endpoint,
            application_key=app_key,
            application_secret=app_secret,
            consumer_key=consumer_key,
        )
    except Exception as e:
        print(f"❌ Erreur de lecture des variables : {e}")
        sys.exit(1)


def get_public_ip():
    print("🔍 Récupération de votre IP publique...")
    try:
        ip = requests.get('https://api.ipify.org', timeout=5).text
        print(f"✅ IP trouvée : {ip}")
        return ip
    except requests.RequestException as e:
        print(f"❌ Erreur lors de la récupération de l'IP : {e}")
        sys.exit(1)


def get_domain_record_id(client, domain, subdomain, delete_sub=False):
    full_domain = f"{subdomain}.{domain}"

    try:
        print(f"⚙️  Vérification de {full_domain} sur la zone {domain}...")

        records = client.get(
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
        sys.exit(1)


def display_message(domain, subdomain, base_message, dry_run=False):
    full_domain = f"{subdomain}.{domain}"
    dry_run_message = "[DRY RUN] - " if dry_run else ""
    print(f"{dry_run_message}{base_message} : {full_domain}")


def create(client, domain, subdomain, target_ip, dry_run=False):
    display_message(domain, subdomain, "🔄 Création sous-domaine", dry_run)
    if not dry_run:
        client.post(
            f'/domain/zone/{domain}/record',
            fieldType='A',
            subDomain=subdomain,
            target=target_ip,
            ttl=60)


def delete(client, domain, subdomain, record_id, dry_run=False):
    display_message(domain, subdomain, "🔄 Suppression sous-domaine", dry_run)
    if not dry_run:
        client.delete(f'/domain/zone/{domain}/record/{record_id}')


def update(client, domain, subdomain, record_id, target_ip, dry_run=False):
    display_message(domain, subdomain, "🔄 Mise à jour sous-domaine", dry_run)
    if not dry_run:
        client.put(f'/domain/zone/{domain}/record/{record_id}', target=target_ip, ttl=60)


def refresh_dns(client, domain, subdomain, dry_run=False):
    display_message(domain, subdomain, "🔄 Application des changements (Refresh Zone)...", dry_run)
    if not dry_run:
        client.post(f'/domain/zone/{domain}/refresh')


def main(domain, subdomain, dry_run=False, remove_sub=False, force=False, profile='default',
         ip=None, keep_existing=False):
    client = load_ovh_client(profile)

    try:
        record_id = get_domain_record_id(client, domain, subdomain, remove_sub)

        if record_id != 0 and keep_existing and not remove_sub:
            print("✅ Sous-domaine conservé tel quel (--keep-existing).")
            return

        target_ip = None if remove_sub else (ip or get_public_ip())

        if record_id != 0:
            if remove_sub:
                if force:
                    delete(client, domain, subdomain, record_id, dry_run)
                else:
                    choice = input(f"Êtes-vous sûr de vouloir supprimer le sous-domaine ({subdomain}) ? (o/n) : ")
                    if choice.lower() == 'o':
                        delete(client, domain, subdomain, record_id, dry_run)
                        print("✅ Suppression effectuée.")
                    else:
                        print("❌ Opération annulée.")
                        return
            else:
                update(client, domain, subdomain, record_id, target_ip, dry_run)
        else:
            if remove_sub:
                print(f"❌ Le sous-domaine n'existe pas.")
            else:
                create(client, domain, subdomain, target_ip, dry_run)

        refresh_dns(client, domain, subdomain, dry_run)
    except ovh.exceptions.APIError as e:
        print(f"❌ Erreur API OVH : {e}")
        sys.exit(1)


def ipv4(value):
    try:
        return str(ipaddress.IPv4Address(value))
    except ipaddress.AddressValueError:
        raise argparse.ArgumentTypeError(f"adresse IPv4 invalide : {value}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Outil CLI OVH")

    parser.add_argument("domain", help="Nom de domaine de base (ex : mondomaine.fr)")
    parser.add_argument("subdomain", help="Nom du sous-domaine (ex : vpn)")

    parser.add_argument("-d", "--dry", action="store_true", help="Lance la commande en mode dry run.")
    parser.add_argument("-r", "--remove", action="store_true", help="Supprime le sous-domaine.")
    parser.add_argument("-f", "--force", action="store_true", help="Ne demande pas de confirmation.")
    parser.add_argument("-p", "--profile", default="default", help="Profil de credentials à utiliser (défaut: default).")
    parser.add_argument("-i", "--ip", type=ipv4, help="IP cible (défaut : IP publique de la machine).")
    parser.add_argument("-k", "--keep-existing", action="store_true", help="Ne modifie pas un sous-domaine existant.")

    args = parser.parse_args()

    main(args.domain, args.subdomain, dry_run=args.dry, remove_sub=args.remove, force=args.force, profile=args.profile,
         ip=args.ip, keep_existing=args.keep_existing)