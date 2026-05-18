# ovh-subdomain
Script de création/mise à jour/suppression de sous-domaine chez OVH.

### Installation
```shell
git clone git@github.com:scamilotti1/ovh-subdomain.git
cd ovh-subdomain
pip install -r requirements.txt
```

#### Rendre la commande globale
```shell
sudo ln -s $(pwd)/command.py /usr/local/bin/ovh-sub
```

---

### Configuration

#### Obtenir les identifiants API OVH
Le script a besoin de la permission de modifier votre zone DNS.

Allez sur : https://eu.api.ovh.com/createToken/  
Connectez-vous avec votre compte OVH.
1. Dans "Script name", mettez un nom (ex: DynHost_Python).
2. Dans "Rights" (Droits), ajoutez les règles suivantes pour limiter la sécurité au strict nécessaire :
    * GET /domain/zone/*
    * PUT /domain/zone/*
    * POST /domain/zone/*
3. Cliquez sur Create keys.

Gardez la page ouverte, vous allez devoir copier : Application Key, Application Secret et Consumer Key.

#### Configurer un profil
```shell
./setup.sh -k <APP_KEY> -s <APP_SECRET> -c <CONSUMER_KEY>
```

Cela crée `~/.ovh-sub/default.env`. Les credentials sont stockés en dehors du dépôt avec des permissions restreintes (`chmod 600`).

#### Configurer plusieurs profils
Vous pouvez gérer plusieurs comptes OVH en nommant vos profils avec `-n` :

```shell
./setup.sh -n perso -k <APP_KEY> -s <APP_SECRET> -c <CONSUMER_KEY>
./setup.sh -n pro   -k <APP_KEY> -s <APP_SECRET> -c <CONSUMER_KEY>
```

Cela crée `~/.ovh-sub/perso.env` et `~/.ovh-sub/pro.env`.

---

### Usage
```shell
ovh-sub [domain] [sub_domain] [options]
```

| Option | Description |
|---|---|
| `-r`, `--remove` | Supprime le sous-domaine |
| `-f`, `--force` | Ne demande pas de confirmation |
| `-d`, `--dry` | Dry run (aucune modification appliquée) |
| `-p`, `--profile` | Profil de credentials à utiliser (défaut : `default`) |

#### Exemples
```shell
# Créer ou mettre à jour un sous-domaine (profil par défaut)
ovh-sub mondomaine.fr vpn

# Utiliser un profil spécifique
ovh-sub mondomaine.fr vpn --profile pro

# Supprimer un sous-domaine avec confirmation
ovh-sub mondomaine.fr vpn --remove

# Supprimer sans confirmation
ovh-sub mondomaine.fr vpn --remove --force

# Tester sans appliquer
ovh-sub mondomaine.fr vpn --dry
```