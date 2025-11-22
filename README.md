# ovh-subdomain
Script de création/mise à jour/suppréssion de sous-domaine chez ovh. 

### Installation
```shell
git clone git@github.com:scamilotti1/ovh-subdomain.git
```

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

#### Configuration
```shell
./setup.sh -k <APP_KEY> -s <APP_SECRET> -c <CONSUMER_KEY>
```

#### Rendre la commance globale
```shell
sudo ln -s $(pwd)$/command.py  /usr/local/bin/ovh-sub
```

### Usage
```shell
ovh-sub [domain] [sub_domain] 
        [-r] remove sub domain (optionnal) 
        [-f] force apply (optionnal)
        [-d] dry run (optionnal)
```