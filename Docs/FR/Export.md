# Exporter une animation en PNG

`Rendering.export_png` produit une séquence complète à cadence choisie :
60 images à 60 Hz représentent une seconde, quel que soit le temps de calcul
ou d’écriture. L’export attend chaque PNG avant d’avancer la simulation.

L’[exemple AnimationExport](https://github.com/Matanek/Silex-Examples/blob/main/Sources/AnimationExport.sx)
compose un cube animé, un dessin 2D et une interface. Il écrit
`frame-000000.png` à `frame-000059.png`, puis affiche le dossier absolu.
Le [consommateur de vérification](../../Tests/Consumer/Tests/Export.sx)
contrôle aussi chaque pixel d’une scène simple.

## Exporter une application configurée

Ce fragment remplace l’appel à `application.run()` après la configuration
habituelle des plugins et systèmes :

```sx
match (try Rendering.export_png(application, "Frames", frames:60, frames_per_second:60)) {
    failure(error) => { print(error) }
    success(count) => { print("Images écrites : ", count) }
}
```

Le dossier doit être neuf et son parent doit exister. Il est créé avant le
démarrage ; un dossier existant est refusé, même vide. Les fichiers restent
exclusifs si une autre écriture intervient ensuite. Le retour réussi est le
nombre de PNG terminés. L’opération possède la boucle de cette application,
qui ne doit pas avoir déjà été exécutée ; elle n’appelle pas un runner personnalisé.

## Préparer avant l’instant zéro

Le paramètre optionnel `ready:(func(Application) bool)?` est appelé après
`initialize` et `startup`, avant toute simulation. Il peut collecter un travail
de chargement et retourne `true` lorsque les ressources nécessaires sont prêtes.
Pendant l’attente, les événements sont pompés ; aucun système de simulation n’est
rejoué et `FrameTime.delta` reste nul. Le prédicat peut arrêter l’application
pour annuler cette préparation. Il doit terminer rapidement et signaler lui-même
les erreurs de ses ressources.

Le [test de préparation](../../Tests/Consumer/Tests/ExportPreparation.sx)
charge un véritable PNG sur un worker, attend sa disponibilité et l’utilise dans
la première image. Le temps de chargement ne décale pas la pose initiale.

## Temps simulé et pause

Pour N images à la cadence f, les échantillons sont indexés de 0 à N−1 aux
instants i/f, pour une durée de sortie N/f. Le premier pas a un delta nul ;
les suivants ont un delta de 1/f. L’ordre est `pre_update`, `update`,
`post_update`, `render`, puis complétion du PNG avant le pas suivant.
La dernière pose de 60 images à 60 Hz est donc celle de 59/60 s.

`FrameTime`, `Simulation` et les scopes enfants reçoivent la politique de temps
contrôlé. Les plugins Animation et Physics l’utilisent normalement ; les pas
fixes physiques dus sont terminés avant le rendu, sans la limite de rattrapage
de la boucle temps réel. Une pause de simulation produit des poses répétées,
sans arrêter la numérotation des images ; les systèmes `always` suivent leur
politique habituelle. Les horloges murales de `STD.Time.Clock`, les entrées et
les graines aléatoires restent sous la responsabilité de la scène.
Les systèmes ne doivent pas remplacer eux-mêmes `FrameTime.delta` pendant cet export.

Les deltas et les consommateurs graphiques emploient les flottants actuels du
moteur : de petits écarts d’arrondi sont possibles. La répétabilité qualifiée
porte sur la même scène et le même environnement, pas sur une identité binaire
universelle entre GPU. Les marqueurs plats des tests se comparent exactement ;
les poses numériques ont une tolérance explicite.

## Attente, erreurs et arrêt

La capture conserve au plus une image en vol et sa limite de transfert PNG de
64 Mio. L’attente fait progresser GPU et encodage sans rejouer les passes de
rendu ni la simulation ; les événements de fenêtre restent traités.
Cet export hors ligne peut prendre plus de temps que la durée
produite ; il ne fournit pas de fichier vidéo.

`application.stop()` annule l’export. La fermeture termine le cycle de vie et
annule ou draine l’écriture courante selon le contrat de [capture PNG](Capture.md).
Les PNG déjà terminés restent disponibles. Un échec ne devient jamais un succès :
le message indique le nombre d’images terminées. Une préparation qui ne devient
jamais prête doit fournir sa propre condition d’arrêt.

Le chemin utilise actuellement une fenêtre et une session graphique compatibles
avec le renderer. `presentation:false` permet de ne pas présenter chaque image ;
une fenêtre cachée convient à l’export automatisé. Cela ne garantit pas une
exécution sans serveur graphique. Aucun son ni capture du bureau.

[Revenir au rendu](README.md).
