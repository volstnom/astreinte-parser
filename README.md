# Script de Gestion du Planning d'Astreintes

Ce script permet de récupérer les informations principales du planning d'astreintes à partir d'un fichier source, de compiler ces informations dans un calendrier, puis d'envoyer par e-mail des invitations correspondant aux créneaux d'astreintes des personnes concernées.

## Fonctionnalités

- Extraction des données du fichier de planning au format Excel.
- Compilation des informations dans une classe exploitable pour un calendrier.
- Envoi d'invitations par e-mail aux participants selon la configuration.

## Installation

1. Clonez ce dépôt sur votre machine locale :
   ```bash
   git clone https://github.com/volstnom/astreinte-parser.git
   ```

2. Installez les dépendances :
   ```bash
   pip install -r requirements.txt
   ```
   Nota : Ce script a été développé en utilisant la version 3.9 de python

## Configuration

Le script nécessite un fichier de configuration YAML pour fonctionner. Voici un exemple de fichier `config.yaml` :

```yaml
path_planning_xls: "C:\\Users\\BPE\\_.xlsm"
year: "2025"
provider:
  email: "example@gmail.com"
  app_password: "abcdefghijklmbop"
attendees:
  - email: "1234@sample.com"
    trigram: "XBR"
    constraints:
    - company: "*"
      max: 4
    - company: "GLS*"
      max: 1
  - email: "5678@sample.com"
    trigram: "ABC"
    constraints:
    - company: "*"
      max: 6
    - company: "*DPD*"
      max: 2
    - company: "*COLLISSIMO*"
      max: 2
```

### Détails des champs de configuration

- `path_planning_xls` : Chemin vers le fichier Excel contenant le planning d'astreintes.
- `year` : Année cible pour l'extraction des données.
- `provider` : Informations sur l'adresse e-mail utilisée pour envoyer les invitations.
  - `email` : Adresse e-mail de l'expéditeur.
  - `app_password` : Mot de passe d'application ou clé d'accès pour l'expéditeur.
- `attendees` : Liste des personnes concernées par les astreintes.
  - `email` : Adresse e-mail de la personne recevant les invitations.
  - `trigram` : Identifiant de l'utilisateur dans le fichier de planning.
  - `constraints` : Contraintes liées à l'utilisateur, spécifiées par :
    - `company` : Motif (wildcard `*` accepté) pour filtrer les sociétés concernées.
    - `max` : Nombre maximum d'astreintes autorisé pour ce motif.

### Utilisation et paramètres de ligne de commande

Le script prend en charge plusieurs arguments de ligne de commande pour contrôler son comportement. Ces arguments permettent d'exécuter des actions spécifiques ou de modifier les données générées.

#### Liste des arguments

| Argument        | Description                                                                                          | Exemple de commande                              |
|-----------------|------------------------------------------------------------------------------------------------------|-------------------------------------------------|
| `--dry-run`     | Exécute le script en mode simulation. Aucune modification n'est appliquée, mais les actions prévues sont affichées. | `python script.py --dry-run`                    |
| `--force`       | Ignore les données existantes dans la base de données et régénère toutes les informations.           | `python script.py --force`                      |
| `--clear-all`   | Supprime toutes les invitations existantes et vide complètement la base de données.                  | `python script.py --clear-all`                  |

#### Exemples d'utilisation

1. **Exécution en mode simulation**  
   ```bash
   python script.py --dry-run
   ```
   Cette commande permet de visualiser les modifications qui seraient effectuées sans les appliquer réellement.

2. **Régénération complète des données**  
   ```bash
   python script.py --force
   ```
   Cette commande force la régénération de toutes les données en ignorant celles déjà stockées en base.

3. **Suppression de toutes les données existantes**  
   ```bash
   python script.py --clear-all
   ```
   Cette commande annule toutes les invitations calendrier et vide la base de données.

### Obtenir un mot de passe d'application via Gmail

Pour configurer l'envoi d'e-mails dans ce script, vous devez utiliser un mot de passe d'application si votre compte Gmail utilise l'authentification à deux facteurs (2FA). Voici les étapes à suivre pour générer un mot de passe d'application :

1. **Activer l'authentification à deux facteurs (si ce n'est pas encore fait)** :
   - Connectez-vous à votre compte Gmail.
   - Accédez à [votre page de sécurité Google](https://myaccount.google.com/security).
   - Sous la section **Connexion à Google**, activez l'**Authentification à deux facteurs**.
   - Suivez les instructions pour configurer 2FA si ce n'est pas encore fait.

2. **Générer un mot de passe d'application** :
   - Une fois 2FA activé, revenez à [votre page de sécurité Google](https://myaccount.google.com/security).
   - Sous la section **Connexion à Google**, cliquez sur **Mots de passe d'application**.
   - Vous serez peut-être invité à entrer votre mot de passe pour confirmer.
   - Dans le menu déroulant, sélectionnez :
     - **Sélectionner une application** : Choisissez `Autre (nom personnalisé)` et entrez un nom (par ex. "Script Astreinte").
     - Cliquez sur **Générer**.

3. **Notez et utilisez le mot de passe généré** :
   - Google affichera un mot de passe d'application unique (une chaîne de 16 caractères).
   - Copiez ce mot de passe et utilisez-le dans le champ `app_password` du fichier de configuration.

4. **Conserver ce mot de passe en sécurité** :
   - Ne partagez pas ce mot de passe.
   - Si vous n'avez plus besoin de ce script, vous pouvez révoquer le mot de passe d'application depuis la même page.

Ce mot de passe d'application permettra au script d'envoyer des e-mails via Gmail sans compromettre votre mot de passe principal.
