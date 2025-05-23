import os
import re
import mutagen
from mutagen.id3 import ID3, TALB, TIT2, TRCK, APIC, TPE1, TPE2
from mutagen.mp3 import MP3
from mutagen.flac import FLAC
from mutagen.mp4 import MP4

def main():
    # Demander le nom de l'album à l'utilisateur
    album_name = input("Entrez le nom de l'album: ")

    # Demander le nom de l'interprète de l'album (Album Artist) seulement
    album_artist_name = input("Entrez le nom de l'interprète de l'album: ")

    # Extensions de fichiers musicaux à traiter
    music_extensions = ['.mp3', '.flac', '.m4a', '.ogg', '.wav']

    # Chemin vers la pochette d'album
    cover_path = "Pochette.jpg"

    # Variable pour savoir si on a une pochette
    has_cover = False
    cover_data = None

    # Vérifier si la pochette existe
    if os.path.exists(cover_path):
        # Lire le contenu de la pochette
        try:
            with open(cover_path, "rb") as cover_file:
                cover_data = cover_file.read()
            has_cover = True
            print(f"Pochette trouvée: {cover_path}")
        except Exception as e:
            print(f"Erreur lors de la lecture de la pochette: {e}")
    else:
        print(f"Aucune pochette trouvée à '{cover_path}'. Les images existantes seront supprimées.")

    # Récupérer tous les fichiers musicaux
    music_files = []
    for filename in os.listdir('.'):
        if os.path.isfile(filename) and any(filename.lower().endswith(ext) for ext in music_extensions):
            music_files.append(filename)

    # Trier les fichiers par ordre alphabétique
    music_files.sort()

    # Créer un dictionnaire pour stocker les numéros de piste des fichiers sans numéro explicite
    auto_track_numbers = {}
    current_track = 1

    # Premier passage: identifier les fichiers qui n'ont pas de numéro
    for filename in music_files:
        track_match = re.match(r'^(\d+)-(.+)', filename)
        if not track_match:
            auto_track_numbers[filename] = str(current_track)
            current_track += 1

    # Parcourir tous les fichiers musicaux
    for filename in music_files:
        file_path = os.path.join('.', filename)

        # Vérifier d'abord si le fichier a déjà un numéro de piste dans ses tags
        existing_track_number = get_existing_track_number(file_path)

        # Si un numéro existe déjà dans les tags, l'utiliser
        if existing_track_number:
            track_number = existing_track_number
            print(f"Numéro de piste existant conservé ({track_number}) pour: {filename}")
        else:
            # Extraire le numéro de piste à partir du nom de fichier si le format est "numero-"
            track_match = re.match(r'^(\d+)-(.+)', filename)

            if track_match:
                track_number = track_match.group(1)
                # Le titre sans le numéro
                title = track_match.group(2)
                # Enlever l'extension et remplacer les tirets par des espaces
                title = os.path.splitext(title)[0].replace('-', ' ')
            else:
                # Si pas de numéro, utiliser le nom du fichier sans extension comme titre
                title = os.path.splitext(filename)[0]
                # Utiliser le numéro de piste automatique basé sur l'ordre alphabétique
                track_number = auto_track_numbers[filename]

        try:
            # Si le titre n'a pas été défini (dans le cas où on a gardé le numéro existant)
            if 'title' not in locals():
                # Extraire le titre du nom de fichier
                track_match = re.match(r'^(\d+)-(.+)', filename)
                if track_match:
                    title = track_match.group(2)
                    title = os.path.splitext(title)[0].replace('-', ' ')
                else:
                    title = os.path.splitext(filename)[0]

            # Traiter en fonction du type de fichier
            if filename.lower().endswith('.mp3'):
                update_mp3_tags(file_path, album_name, title, track_number, cover_data, album_artist_name, has_cover)
            elif filename.lower().endswith('.flac'):
                update_flac_tags(file_path, album_name, title, track_number, cover_data, album_artist_name, has_cover)
            elif filename.lower().endswith('.m4a'):
                update_m4a_tags(file_path, album_name, title, track_number, cover_data, album_artist_name, has_cover)
            else:
                print(f"Format non pris en charge pour les tags: {filename}")
                continue

            print(f"Mis à jour: {filename}")

        except Exception as e:
            print(f"Erreur lors de la mise à jour de {filename}: {e}")

        # Réinitialiser la variable title pour le prochain fichier
        if 'title' in locals():
            del title

def get_existing_track_number(file_path):
    """Récupère le numéro de piste existant dans les tags du fichier"""
    try:
        if file_path.lower().endswith('.mp3'):
            try:
                tags = ID3(file_path)
                if "TRCK" in tags:
                    track = tags["TRCK"].text[0]
                    # Si le format est "1/10", ne garder que le numéro avant le slash
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
                    # trkn est un tuple (numéro, total)
                    return str(audio["trkn"][0][0])
            except:
                pass
    except Exception as e:
        print(f"Erreur lors de la lecture des tags existants pour {os.path.basename(file_path)}: {e}")

    return None

def update_mp3_tags(file_path, album_name, title, track_number, cover_data, album_artist_name, has_cover):
    """Mettre à jour les tags d'un fichier MP3"""
    try:
        tags = ID3(file_path)
    except:
        # Si le fichier n'a pas de tags ID3, en créer
        tags = ID3()

    # Définir les tags
    tags["TALB"] = TALB(encoding=3, text=[album_name])
    tags["TIT2"] = TIT2(encoding=3, text=[title])

    # NE PAS toucher à l'interprète principal (TPE1)

    # Gérer l'interprète de l'album (Album Artist)
    if album_artist_name:
        # Remplacer l'interprète de l'album
        tags["TPE2"] = TPE2(encoding=3, text=[album_artist_name])
        print(f"Interprète de l'album mis à jour pour: {os.path.basename(file_path)}")

    # Gestion de la pochette
    # Supprimer TOUTES les images existantes (APIC, incluant prévisualisations)
    for key in list(tags.keys()):
        if key.startswith('APIC'):
            del tags[key]
            print(f"Image/prévisualisation supprimée pour: {os.path.basename(file_path)}")

    # Ajouter la nouvelle pochette seulement si disponible
    if has_cover and cover_data:
        tags["APIC"] = APIC(
            encoding=3,           # UTF-8
            mime="image/jpeg",    # Type MIME
            type=3,               # 3 est pour la pochette de l'album
            desc="Cover",
            data=cover_data
        )
        print(f"Nouvelle pochette ajoutée pour: {os.path.basename(file_path)}")

    # Définir le numéro de piste
    if track_number:
        tags["TRCK"] = TRCK(encoding=3, text=[track_number])

    # Sauvegarder les tags
    tags.save(file_path)

def update_flac_tags(file_path, album_name, title, track_number, cover_data, album_artist_name, has_cover):
    """Mettre à jour les tags d'un fichier FLAC"""
    audio = FLAC(file_path)

    # Définir les tags
    audio["album"] = album_name
    audio["title"] = title

    # NE PAS toucher à l'interprète principal (artist)

    # Gérer l'interprète de l'album (Album Artist)
    if album_artist_name:
        # Remplacer l'interprète de l'album
        audio["albumartist"] = album_artist_name
        print(f"Interprète de l'album mis à jour pour: {os.path.basename(file_path)}")

    # Définir le numéro de piste
    if track_number:
        audio["tracknumber"] = track_number

    # Gestion de la pochette
    # Toujours supprimer toutes les images existantes
    if audio.pictures:
        audio.clear_pictures()
        print(f"Images/prévisualisations supprimées pour: {os.path.basename(file_path)}")

    # Ajouter la nouvelle pochette seulement si disponible
    if has_cover and cover_data:
        picture = mutagen.flac.Picture()
        picture.type = 3  # 3 est pour la pochette de l'album
        picture.mime = "image/jpeg"
        picture.desc = "Cover"
        picture.data = cover_data

        audio.add_picture(picture)
        print(f"Nouvelle pochette ajoutée pour: {os.path.basename(file_path)}")

    # Sauvegarder les tags
    audio.save()

def update_m4a_tags(file_path, album_name, title, track_number, cover_data, album_artist_name, has_cover):
    """Mettre à jour les tags d'un fichier M4A"""
    audio = MP4(file_path)

    # Définir les tags
    audio["\xa9alb"] = [album_name]
    audio["\xa9nam"] = [title]

    # NE PAS toucher à l'interprète principal (\xa9ART)

    # Gérer l'interprète de l'album (Album Artist)
    if album_artist_name:
        # Remplacer l'interprète de l'album
        audio["aART"] = [album_artist_name]
        print(f"Interprète de l'album mis à jour pour: {os.path.basename(file_path)}")

    # Définir le numéro de piste
    if track_number:
        audio["trkn"] = [(int(track_number), 0)]

    # Gestion de la pochette
    if "covr" in audio:
        del audio["covr"]
        print(f"Images/prévisualisations supprimées pour: {os.path.basename(file_path)}")

    # Ajouter la nouvelle pochette seulement si disponible
    if has_cover and cover_data:
        audio["covr"] = [cover_data]
        print(f"Nouvelle pochette ajoutée pour: {os.path.basename(file_path)}")

    # Sauvegarder les tags
    audio.save()

if __name__ == "__main__":
    main()