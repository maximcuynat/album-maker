#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import sys
from ReName import ReName
from ReOrder import ReOrder

def main():
    parser = argparse.ArgumentParser(description="Utilitaire de gestion des métadonnées et organisation des fichiers musicaux")
    subparsers = parser.add_subparsers(dest='command', help='Commandes disponibles')

    # Sous-commande rename
    rename_parser = subparsers.add_parser('rename', help='Mettre à jour les métadonnées des fichiers musicaux')
    rename_parser.add_argument('--album', required=True, help='Nom de l\'album')
    rename_parser.add_argument('--artist', required=True, help='Nom de l\'interprète de l\'album')

    # Sous-commande reorder
    reorder_parser = subparsers.add_parser('reorder', help='Organiser les fichiers musicaux par artiste/album')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    try:
        if args.command == 'rename':
            renamer = ReName()
            renamer.process_files(args.album, args.artist)
        elif args.command == 'reorder':
            organizer = ReOrder()
            organizer.organize_music()
    except ImportError as e:
        print(f"Erreur d'importation: {e}")
        print("Assurez-vous que les modules 'rename.py' et 'reorder.py' sont présents et que mutagen est installé.")
        sys.exit(1)
    except Exception as e:
        print(f"Erreur: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()