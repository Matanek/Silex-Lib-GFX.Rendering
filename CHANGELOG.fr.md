# Historique des changements

## [0.5.0] - 2026-11-08

- `record_mp4(..., audio:audio)` inclut le mix du périphérique avec file bornée et worker audio distinct, chronologie entière, mux AAC sans réencodage vidéo et échec explicite en cas de saturation ou d’horloge incohérente.

- `export_mp4(..., audio:audio)` inclut le mix Audio.offline dans une piste AAC synchronisée : arrondi cumulé, rendu/écriture par blocs sur worker, finalisation et nettoyage des deux pistes. Les exports muets restent compatibles.

- `Renderer.record_mp4` enregistre le rendu composé pendant le jeu : session possédée, arrêt/finalisation asynchrones, file bornée, durée réelle avec duplication et compteurs, annulation et erreurs récupérables. FFmpeg reste explicite ; aucun transfert en capture inactive.

- `export_mp4` produit une vidéo sans son à temps contrôlé avec un FFmpeg explicitement choisi : MP4/MPEG-4 Part 2/YUV420P, séquence PNG temporaire, sortie exclusive, annulation et nettoyage.

- `export_png` produit une séquence indexée à temps contrôlé, attend la préparation avant t=0 et conserve les PNG terminés en cas d’arrêt ou d’erreur.

- `Renderer.capture_png` enregistre le prochain rendu complet, résolu après MSAA,
  avec ticket, annulation, erreurs récupérables et sortie exclusive. Mapping,
  copie CPU, PNG et écriture utilisent un worker dédié ; aucune lecture GPU
  n'est déclenchée sans capture. Hors écran, l'alpha est préservé ; en présentation,
  la sortie est opaque. Limite : une opération et 64 Mio de transfert par renderer.
