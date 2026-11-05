# Historique des changements

## [Unreleased]

- `export_png` produit une séquence indexée à temps contrôlé, attend la préparation avant t=0 et conserve les PNG terminés en cas d’arrêt ou d’erreur.

- `Renderer.capture_png` enregistre le prochain rendu complet, résolu après MSAA,
  avec ticket, annulation, erreurs récupérables et sortie exclusive. Mapping,
  copie CPU, PNG et écriture utilisent un worker dédié ; aucune lecture GPU
  n'est déclenchée sans capture. Hors écran, l'alpha est préservé ; en présentation,
  la sortie est opaque. Limite : une opération et 64 Mio de transfert par renderer.
