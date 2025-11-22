# ovh-subdomain
Script de création/mise à jour/suppréssion de sous-domaine chez ovh. 

## Obtenir les identifiants API OVH
Le script a besoin de la permission de modifier votre zone DNS.

Allez sur : https://eu.api.ovh.com/createToken/

Connectez-vous avec votre compte OVH.

```shell
./setup.sh -k <APP_KEY> -s <APP_SECRET> -c <CONSUMER_KEY>
```

## Usage
```shell
ovh-sub [domain] [sub_domain] 
        [-r] remove sub domain (optionnal) 
        [-f] force apply (optionnal)
        [-d] dry run (optionnal)
```