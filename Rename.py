import os
import re
import mutagen
from mutagen.id3 import ID3, TALB, TIT2, TRCK, APIC, TPE1, TPE2
from mutagen.mp3 import MP3
from mutagen.flac import FLAC
from mutagen.mp4 import MP4

class ReName:
    def __init__(self):
        self.music_extensions = ['.mp3', '.flac', '.m4a', '.ogg', '.wav']
        self.cover_path = "Pochette.jpg"

    def process_files(self, album_name, album_artist_name):
        has_cover, cover_data = self._load_cover()
        music_files = self._get_music_files()
        auto_track_numbers = self._assign_auto_track_numbers(music_files)

        for filename in music_files:
            file_path = os.path.join('.', filename)
            existing_track_number = self._get_existing_track_number(file_path)

            if existing_track_number:
                track_number = existing_track_number
                print(f"Numéro de piste existant conservé ({track_number}) pour: {filename}")
            else:
                track_match = re.match(r'^(\d+)-(.+)', filename)
                if track_match:
                    track_number = track_match.group(1)
                    title = track_match.group(2)
                    title = os.path.splitext(title)[0].replace('-', ' ')
                else:
                    title = os.path.splitext(filename)[0]
                    track_number = auto_track_numbers[filename]

            try:
                if 'title' not in locals():
                    track_match = re.match(r'^(\d+)-(.+)', filename)
                    if track_match:
                        title = track_match.group(2)
                        title = os.path.splitext(title)[0].replace('-', ' ')
                    else:
                        title = os.path.splitext(filename)[0]

                if filename.lower().endswith('.mp3'):
                    self._update_mp3_tags(file_path, album_name, title, track_number, cover_data, album_artist_name, has_cover)
                elif filename.lower().endswith('.flac'):
                    self._update_flac_tags(file_path, album_name, title, track_number, cover_data, album_artist_name, has_cover)
                elif filename.lower().endswith('.m4a'):
                    self._update_m4a_tags(file_path, album_name, title, track_number, cover_data, album_artist_name, has_cover)
                else:
                    print(f"Format non pris en charge pour les tags: {filename}")
                    continue

                print(f"Mis à jour: {filename}")

            except Exception as e:
                print(f"Erreur lors de la mise à jour de {filename}: {e}")

            if 'title' in locals():
                del title

    def _load_cover(self):
        has_cover = False
        cover_data = None

        if os.path.exists(self.cover_path):
            try:
                with open(self.cover_path, "rb") as cover_file:
                    cover_data = cover_file.read()
                has_cover = True
                print(f"Pochette trouvée: {self.cover_path}")
            except Exception as e:
                print(f"Erreur lors de la lecture de la pochette: {e}")
        else:
            print(f"Aucune pochette trouvée à '{self.cover_path}'. Les images existantes seront supprimées.")

        return has_cover, cover_data

    def _get_music_files(self):
        music_files = []
        for filename in os.listdir('.'):
            if os.path.isfile(filename) and any(filename.lower().endswith(ext) for ext in self.music_extensions):
                music_files.append(filename)
        music_files.sort()
        return music_files

    def _assign_auto_track_numbers(self, music_files):
        auto_track_numbers = {}
        current_track = 1

        for filename in music_files:
            track_match = re.match(r'^(\d+)-(.+)', filename)
            if not track_match:
                auto_track_numbers[filename] = str(current_track)
                current_track += 1

        return auto_track_numbers

    def _get_existing_track_number(self, file_path):
        try:
            if file_path.lower().endswith('.mp3'):
                try:
                    tags = ID3(file_path)
                    if "TRCK" in tags:
                        track = tags["TRCK"].text[0]
                        if '/' in track:
                            track = track.split('/')[0]
                        return track
                except:
                    pass
            elif file_path.lower().endswith('.flac'):
                try:
                    audio = FLAC(file_path)
                    if "tracknumber" in audio:
                        track = audio["tracknumber"][0]
                        if '/' in track:
                            track = track.split('/')[0]
                        return track
                except:
                    pass
            elif file_path.lower().endswith('.m4a'):
                try:
                    audio = MP4(file_path)
                    if "trkn" in audio:
                        return str(audio["trkn"][0][0])
                except:
                    pass
        except Exception as e:
            print(f"Erreur lors de la lecture des tags existants pour {os.path.basename(file_path)}: {e}")

        return None

    def _update_mp3_tags(self, file_path, album_name, title, track_number, cover_data, album_artist_name, has_cover):
        try:
            tags = ID3(file_path)
        except:
            tags = ID3()

        tags["TALB"] = TALB(encoding=3, text=[album_name])
        tags["TIT2"] = TIT2(encoding=3, text=[title])

        if album_artist_name:
            tags["TPE2"] = TPE2(encoding=3, text=[album_artist_name])
            print(f"Interprète de l'album mis à jour pour: {os.path.basename(file_path)}")

        for key in list(tags.keys()):
            if key.startswith('APIC'):
                del tags[key]
                print(f"Image/prévisualisation supprimée pour: {os.path.basename(file_path)}")

        if has_cover and cover_data:
            tags["APIC"] = APIC(
                encoding=3,
                mime="image/jpeg",
                type=3,
                desc="Cover",
                data=cover_data
            )
            print(f"Nouvelle pochette ajoutée pour: {os.path.basename(file_path)}")

        if track_number:
            tags["TRCK"] = TRCK(encoding=3, text=[track_number])

        tags.save(file_path)

    def _update_flac_tags(self, file_path, album_name, title, track_number, cover_data, album_artist_name, has_cover):
        audio = FLAC(file_path)

        audio["album"] = album_name
        audio["title"] = title

        if album_artist_name:
            audio["albumartist"] = album_artist_name
            print(f"Interprète de l'album mis à jour pour: {os.path.basename(file_path)}")

        if track_number:
            audio["tracknumber"] = track_number

        if audio.pictures:
            audio.clear_pictures()
            print(f"Images/prévisualisations supprimées pour: {os.path.basename(file_path)}")

        if has_cover and cover_data:
            picture = mutagen.flac.Picture()
            picture.type = 3
            picture.mime = "image/jpeg"
            picture.desc = "Cover"
            picture.data = cover_data

            audio.add_picture(picture)
            print(f"Nouvelle pochette ajoutée pour: {os.path.basename(file_path)}")

        audio.save()

    def _update_m4a_tags(self, file_path, album_name, title, track_number, cover_data, album_artist_name, has_cover):
        audio = MP4(file_path)

        audio["\xa9alb"] = [album_name]
        audio["\xa9nam"] = [title]

        if album_artist_name:
            audio["aART"] = [album_artist_name]
            print(f"Interprète de l'album mis à jour pour: {os.path.basename(file_path)}")

        if track_number:
            audio["trkn"] = [(int(track_number), 0)]

        if "covr" in audio:
            del audio["covr"]
            print(f"Images/prévisualisations supprimées pour: {os.path.basename(file_path)}")

        if has_cover and cover_data:
            audio["covr"] = [cover_data]
            print(f"Nouvelle pochette ajoutée pour: {os.path.basename(file_path)}")

        audio.save()