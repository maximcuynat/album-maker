# Music Metadata Manager

Un utilitaire Python pour la gestion des métadonnées et l'organisation des fichiers musicaux. Cet outil permet de mettre à jour les tags ID3/FLAC/MP4 et d'organiser automatiquement votre collection musicale.

## Fonctionnalités

### 🏷️ Gestion des métadonnées (ReName)
- Mise à jour des tags pour MP3, FLAC, M4A, OGG, WAV
- Support des pochettes d'album (JPEG)
- Numérotation automatique des pistes
- Préservation des artistes principaux existants
- Gestion intelligente des titres basée sur les noms de fichiers

### 📁 Organisation automatique (ReOrder)
- Organisation par structure Artiste/Album
- Basé sur les métadonnées "Album Artist"
- Support multi-formats
- Gestion des caractères spéciaux dans les noms
- Logging détaillé des opérations

## Installation

### Prérequis
```bash
pip install mutagen
```

### Clonage du projet
```bash
git clone https://github.com/maximcuynat/album-maker.git
cd music-metadata-manager
```

## Utilisation

### Interface en ligne de commande

#### Mise à jour des métadonnées
```bash
python main.py rename --album "Nom de l'Album" --artist "Artiste de l'Album"
```

#### Organisation des fichiers
```bash
python main.py reorder
```

### Utilisation programmatique

```python
from rename import ReName
from reorder import ReOrder

# Mise à jour des métadonnées
renamer = ReName()
renamer.process_files("Mon Album", "Mon Artiste")

# Organisation des fichiers
organizer = ReOrder()
organizer.organize_music()
```

## Formats supportés

| Format | Extension | Métadonnées | Pochettes |
|--------|-----------|-------------|-----------|
| MP3    | .mp3      | ✅ ID3v2    | ✅ APIC   |
| FLAC   | .flac     | ✅ Vorbis   | ✅ Picture |
| M4A/AAC| .m4a/.aac | ✅ MP4      | ✅ covr   |
| OGG    | .ogg      | ✅ Vorbis   | ❌        |
| WAV    | .wav      | ✅ ID3      | ❌        |

## Structure des fichiers

### Convention de nommage
```
01-Titre de la chanson.mp3
02-Autre chanson.mp3
Pochette.jpg
```

### Organisation générée
```
Artiste/
├── Album 1/
│   ├── 01-Chanson.mp3
│   └── 02-Autre chanson.mp3
└── Album 2/
    └── 01-Titre.flac
```

## Options avancées

### Gestion des numéros de piste
- **Fichiers préfixés** : `01-titre.mp3` → Piste 1
- **Métadonnées existantes** : Priorité aux tags existants
- **Attribution automatique** : Ordre alphabétique pour les autres

### Gestion des pochettes
- **Fichier requis** : `Pochette.jpg` dans le dossier courant
- **Formats supportés** : JPEG
- **Comportement** : Remplacement automatique des images existantes

### Métadonnées préservées
- **Artiste principal** : Conservé tel quel
- **Album Artist** : Mis à jour avec la valeur fournie
- **Titre** : Extrait du nom de fichier ou conservé
- **Numéro de piste** : Détection intelligente

## Logging

Le module ReOrder utilise le logging Python standard :
```
2025-01-XX XX:XX:XX - INFO - Organisation basée sur la métadonnée 'Interprète de l'album'
2025-01-XX XX:XX:XX - INFO - Trouvé 15 fichiers musicaux à organiser
2025-01-XX XX:XX:XX - INFO - Déplacé: song.mp3 -> Artist/Album/
```

## Gestion d'erreurs

- **Fichiers corrompus** : Ignorés avec message d'erreur
- **Permissions insuffisantes** : Erreur explicite
- **Formats non supportés** : Avertissement et passage au suivant
- **Fichiers existants** : Évitement des doublons

## Exemples d'utilisation

### Workflow complet
```bash
# 1. Placer les fichiers musicaux et Pochette.jpg dans un dossier
# 2. Mettre à jour les métadonnées
python main.py rename --album "The Dark Side of the Moon" --artist "Pink Floyd"

# 3. Organiser dans la structure de dossiers
python main.py reorder
```

### Cas d'usage spécifiques

#### Album multi-artistes
```bash
# L'artiste principal de chaque piste est préservé
# Seul l'Album Artist est unifié
python main.py rename --album "Compilation 2025" --artist "Various Artists"
```

#### Renommage par lots
```bash
#!/bin/bash
for dir in */; do
    cd "$dir"
    python ../main.py rename --album "${dir%/}" --artist "Mon Artiste"
    cd ..
done
```

## Limitations

- Les pochettes doivent être au format JPEG
- Le nom de fichier pochette est fixe : `Pochette.jpg`
- Formats OGG et WAV : pas de support pochettes intégrées
- Traitement uniquement du dossier courant (non récursif)

## Contribution

Les contributions sont les bienvenues ! Veuillez :
1. Fork le projet
2. Créer une branche feature (`git checkout -b feature/nouvelle-fonctionnalite`)
3. Commit vos changements (`git commit -am 'Ajout nouvelle fonctionnalité'`)
4. Push vers la branche (`git push origin feature/nouvelle-fonctionnalite`)
5. Créer une Pull Request

## Licence

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.

## Support

Pour signaler un bug ou demander une fonctionnalité, veuillez ouvrir une [issue](https://github.com/maximcuynat/album-maker/issues).

---

⭐ Si ce projet vous est utile, n'hésitez pas à lui donner une étoile sur GitHub !