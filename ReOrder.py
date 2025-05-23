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

class ReOrder:
    def __init__(self):
        self.music_extensions = ['.mp3', '.flac', '.m4a', '.aac', '.ogg', '.wav']
        self._setup_logging()

    def _setup_logging(self):
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger(__name__)
        self.logger.info("Organisation basée sur la métadonnée 'Interprète de l'album' (album_artist)")

    def organize_music(self):
        current_dir = Path('.')
        processed_count = 0
        skipped_count = 0

        music_files = []
        for ext in self.music_extensions:
            music_files.extend(list(current_dir.glob(f"*{ext}")))

        if not music_files:
            self.logger.info("Aucun fichier musical trouvé dans le dossier courant.")
            return

        self.logger.info(f"Trouvé {len(music_files)} fichiers musicaux à organiser.")

        for file_path in music_files:
            try:
                if not file_path.is_file():
                    continue

                artist, album = self._get_metadata(file_path)

                artist_dir = current_dir / artist
                album_dir = artist_dir / album

                artist_dir.mkdir(exist_ok=True)
                album_dir.mkdir(exist_ok=True)

                destination = album_dir / file_path.name

                if destination.exists():
                    self.logger.warning(f"Le fichier {file_path.name} existe déjà dans {album_dir}. Ignoré.")
                    skipped_count += 1
                    continue

                shutil.move(str(file_path), str(destination))
                self.logger.info(f"Déplacé: {file_path.name} -> {artist}/{album}/")
                processed_count += 1

            except Exception as e:
                self.logger.error(f"Erreur lors du traitement de {file_path.name}: {str(e)}")
                skipped_count += 1

        self.logger.info(f"Organisation terminée: {processed_count} fichiers traités, {skipped_count} fichiers ignorés.")

    def _get_metadata(self, file_path):
        extension = file_path.suffix.lower()
        artist = "Unknown Artist"
        album = "Unknown Album"

        try:
            if extension == '.mp3':
                try:
                    audio = EasyID3(file_path)
                    if 'albumartist' in audio and audio['albumartist']:
                        artist = audio['albumartist'][0]
                    elif 'performer' in audio and audio['performer']:
                        artist = audio['performer'][0]
                    if 'album' in audio and audio['album']:
                        album = audio['album'][0]
                except mutagen.id3.ID3NoHeaderError:
                    audio = MP3(file_path)

            elif extension == '.flac':
                audio = FLAC(file_path)
                if 'albumartist' in audio and audio['albumartist']:
                    artist = audio['albumartist'][0]
                elif 'album artist' in audio and audio['album artist']:
                    artist = audio['album artist'][0]
                if 'album' in audio and audio['album']:
                    album = audio['album'][0]

            elif extension == '.m4a' or extension == '.aac':
                audio = MP4(file_path)
                if 'aART' in audio and audio['aART']:
                    artist = audio['aART'][0]
                elif '©ART' in audio and audio['©ART']:
                    artist = audio['©ART'][0]
                if '©alb' in audio and audio['©alb']:
                    album = audio['©alb'][0]

            elif extension == '.ogg':
                audio = mutagen.File(file_path)
                if 'albumartist' in audio and audio['albumartist']:
                    artist = audio['albumartist'][0]
                elif 'album_artist' in audio and audio['album_artist']:
                    artist = audio['album_artist'][0]
                elif 'album artist' in audio and audio['album artist']:
                    artist = audio['album artist'][0]
                if 'album' in audio and audio['album']:
                    album = audio['album'][0]

            else:
                audio = mutagen.File(file_path)
                if audio and hasattr(audio, 'tags') and audio.tags:
                    for tag in ['albumartist', 'album_artist', 'album artist', 'performer']:
                        if tag in audio.tags:
                            artist = audio.tags[tag][0]
                            break
                    if 'album' in audio.tags:
                        album = audio.tags['album'][0]

        except Exception as e:
            self.logger.error(f"Erreur lors de l'extraction des métadonnées de {file_path}: {str(e)}")

        artist = self._clean_filename(artist)
        album = self._clean_filename(album)

        return artist, album

    def _clean_filename(self, name):
        forbidden_chars = ['/', '\\', ':', '*', '?', '"', '<', '>', '|']
        for char in forbidden_chars:
            name = name.replace(char, '_')

        name = ' '.join(name.split())

        if not name.strip():
            name = "Unknown"

        return name