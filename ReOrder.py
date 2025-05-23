#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import shutil
from pathlib import Path
import mutagen
from mutagen.easyid3 import EasyID3
from mutagen.mp3 import MP3
from mutagen.flac import FLAC
from mutagen.mp4 import MP4
import logging

# Configuration du logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Message explicatif sur le tri utilisé
logger.info("Organisation basée sur la métadonnée 'Interprète de l'album' (album_artist)")

# Extensions de fichiers musicaux supportées
MUSIC_EXTENSIONS = ['.mp3', '.flac', '.m4a', '.aac', '.ogg', '.wav']

def get_metadata(file_path):
    """
    Extrait les métadonnées (interprète de l'album et album) d'un fichier musical.
    """
    extension = file_path.suffix.lower()
    artist = "Unknown Artist"
    album = "Unknown Album"

    try:
        if extension == '.mp3':
            try:
                audio = EasyID3(file_path)
                # Utiliser 'albumartist' au lieu de 'artist'
                if 'albumartist' in audio and audio['albumartist']:
                    artist = audio['albumartist'][0]
                elif 'performer' in audio and audio['performer']:  # Alternative
                    artist = audio['performer'][0]
                # Conserver la récupération de l'album
                if 'album' in audio and audio['album']:
                    album = audio['album'][0]
            except mutagen.id3.ID3NoHeaderError:
                # Essayez avec MP3 si EasyID3 échoue
                audio = MP3(file_path)
                # Pour ID3, les tags pour albumartist peuvent varier

        elif extension == '.flac':
            audio = FLAC(file_path)
            # Pour FLAC, privilégier 'albumartist'
            if 'albumartist' in audio and audio['albumartist']:
                artist = audio['albumartist'][0]
            elif 'album artist' in audio and audio['album artist']:
                artist = audio['album artist'][0]
            # Conserver la récupération de l'album
            if 'album' in audio and audio['album']:
                album = audio['album'][0]

        elif extension == '.m4a' or extension == '.aac':
            audio = MP4(file_path)
            # Pour les fichiers MP4/M4A/AAC, rechercher l'équivalent de albumartist
            if 'aART' in audio and audio['aART']:  # Tag albumartist pour MP4
                artist = audio['aART'][0]
            elif '©ART' in audio and audio['©ART']:  # Fallback sur artiste normal
                artist = audio['©ART'][0]
            # Conserver la récupération de l'album
            if '©alb' in audio and audio['©alb']:
                album = audio['©alb'][0]

        elif extension == '.ogg':
            audio = mutagen.File(file_path)
            # Pour OGG, rechercher albumartist ou album_artist
            if 'albumartist' in audio and audio['albumartist']:
                artist = audio['albumartist'][0]
            elif 'album_artist' in audio and audio['album_artist']:
                artist = audio['album_artist'][0]
            elif 'album artist' in audio and audio['album artist']:
                artist = audio['album artist'][0]
            # Conserver la récupération de l'album
            if 'album' in audio and audio['album']:
                album = audio['album'][0]

        else:
            # Pour les autres formats, essayez avec l'approche générique
            audio = mutagen.File(file_path)
            if audio and hasattr(audio, 'tags') and audio.tags:
                # Recherche de variantes de "albumartist"
                for tag in ['albumartist', 'album_artist', 'album artist', 'performer']:
                    if tag in audio.tags:
                        artist = audio.tags[tag][0]
                        break
                # Conserver la récupération de l'album
                if 'album' in audio.tags:
                    album = audio.tags['album'][0]

    except Exception as e:
        logger.error(f"Erreur lors de l'extraction des métadonnées de {file_path}: {str(e)}")

    # Nettoyage des noms pour éviter les problèmes avec le système de fichiers
    artist = clean_filename(artist)
    album = clean_filename(album)

    return artist, album

def clean_filename(name):
    """
    Nettoie les caractères non autorisés dans les noms de fichiers/dossiers.
    """
    # Caractères interdits dans les noms de fichiers
    forbidden_chars = ['/', '\\', ':', '*', '?', '"', '<', '>', '|']
    for char in forbidden_chars:
        name = name.replace(char, '_')

    # Enlever les espaces multiples et les espaces de début/fin
    name = ' '.join(name.split())

    # Si vide, utiliser un nom par défaut
    if not name.strip():
        name = "Unknown"

    return name

def organize_music():
    """
    Fonction principale pour organiser les fichiers musicaux.
    """
    current_dir = Path('.')
    processed_count = 0
    skipped_count = 0

    # Récupération de tous les fichiers musicaux du dossier courant
    music_files = []
    for ext in MUSIC_EXTENSIONS:
        music_files.extend(list(current_dir.glob(f"*{ext}")))

    if not music_files:
        logger.info("Aucun fichier musical trouvé dans le dossier courant.")
        return

    logger.info(f"Trouvé {len(music_files)} fichiers musicaux à organiser.")

    for file_path in music_files:
        try:
            # Ignorer les dossiers
            if not file_path.is_file():
                continue

            # Récupération des métadonnées (utilisera 'Interprète de l'album' au lieu de 'Artiste')
            artist, album = get_metadata(file_path)

            # Création des chemins des dossiers de destination
            artist_dir = current_dir / artist
            album_dir = artist_dir / album

            # Création des dossiers s'ils n'existent pas
            artist_dir.mkdir(exist_ok=True)
            album_dir.mkdir(exist_ok=True)

            # Destination finale du fichier
            destination = album_dir / file_path.name

            # Vérification si le fichier existe déjà à destination
            if destination.exists():
                logger.warning(f"Le fichier {file_path.name} existe déjà dans {album_dir}. Ignoré.")
                skipped_count += 1
                continue

            # Déplacement du fichier
            shutil.move(str(file_path), str(destination))
            logger.info(f"Déplacé: {file_path.name} -> {artist}/{album}/")
            processed_count += 1

        except Exception as e:
            logger.error(f"Erreur lors du traitement de {file_path.name}: {str(e)}")
            skipped_count += 1

    logger.info(f"Organisation terminée: {processed_count} fichiers traités, {skipped_count} fichiers ignorés.")

if __name__ == "__main__":
    try:
        # Vérification de la présence de mutagen
        import mutagen
    except ImportError:
        print("La bibliothèque 'mutagen' est requise mais n'est pas installée.")
        print("Installez-la avec: pip install mutagen")
        exit(1)

    print("Début de l'organisation des fichiers musicaux...")
    organize_music()
    print("Terminé!")