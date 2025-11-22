#!/bin/bash

# Valeur par défaut
ENDPOINT="ovh-eu"
BASE_DIR="$HOME/.ovh-sub"
OUTPUT_FILE="$BASE_DIR/.env"

# Fonction d'aide
usage() {
    echo "Usage: $0 -k APP_KEY -s APP_SECRET -c CONSUMER_KEY [-e ENDPOINT]"
    echo ""
    echo "  -k  OVH Application Key"
    echo "  -s  OVH Application Secret"
    echo "  -c  OVH Consumer Key"
    echo "  -e  Endpoint OVH (défaut: ovh-eu)"
    echo "  -h  Affiche cette aide"
    exit 1
}

# Récupération des arguments
while getopts "k:s:c:e:h" opt; do
    case $opt in
        k) APP_KEY="$OPTARG" ;;
        s) APP_SECRET="$OPTARG" ;;
        c) CONSUMER_KEY="$OPTARG" ;;
        e) ENDPOINT="$OPTARG" ;;
        h) usage ;;
        *) usage ;;
    esac
done

# Vérification que les paramètres obligatoires sont là
if [ -z "$APP_KEY" ] || [ -z "$APP_SECRET" ] || [ -z "$CONSUMER_KEY" ]; then
    echo "❌ Erreur : Il manque des paramètres obligatoires."
    usage
fi

# Création du fichier
echo "⚙️  Génération du fichier $OUTPUT_FILE..."

mkdir $BASE_DIR

cat << EOF > "$OUTPUT_FILE"
OVH_ENDPOINT=$ENDPOINT
OVH_APP_KEY=$APP_KEY
OVH_APP_SECRET=$APP_SECRET
OVH_CONSUMER_KEY=$CONSUMER_KEY
EOF

# Sécurisation du fichier (lecture/écriture uniquement pour l'utilisateur)
chmod 600 "$OUTPUT_FILE"

echo "✅ Fichier créé avec succès !"
echo "🔒 Permissions restreintes (chmod 600) appliquées pour la sécurité."