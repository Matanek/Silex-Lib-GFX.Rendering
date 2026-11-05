# Exporter une animation en MP4

`Rendering.export_mp4` exporte une application configurée en vidéo sans son.
Il conserve les échantillons contrôlés de l’[export PNG](Export.md), encode puis
finalise le conteneur avant de rendre la réussite. Le format initial est
**MP4, MPEG-4 Part 2, YUV420P**, avec une qualité fixée à `q:v=2` et sans images B.
Ce parcours est hors ligne : le temps de calcul ne change pas les poses.

## Fournir l’encodeur

FFmpeg est un programme externe choisi explicitement par le consommateur.
La fonction exige son **chemin absolu**, sans recherche dans PATH, sans shell
et sans téléchargement à l’exécution. Le parent de la sortie doit exister et
le fichier final doit être nouveau.

Après la configuration normale des plugins et systèmes, ce fragment remplace
`application.run()` :

```sx
match (try Rendering.export_mp4(
    application, "Animation.mp4", frames:60,
    ffmpeg:"/chemin/absolu/ffmpeg", frames_per_second:60
)) {
    failure(error) => { print(error) }
    success(count) => { print("Vidéo terminée : ", count, " images") }
}
```

Le paramètre optionnel `ready:(func(Application) bool)?` suit le même contrat
que pour les PNG : préparation après startup, avant l’instant zéro. L’application
ne doit pas avoir déjà été exécutée. Une fenêtre et une session graphique
compatibles restent nécessaires ; une fenêtre cachée convient aux exports automatiques.

## Installer un FFmpeg adapté

La version de qualification est **FFmpeg 9.0.2**, construite depuis les
[sources officielles](https://ffmpeg.org/download.html) avec les parties GPL,
nonfree et version3 désactivées. Ce binaire déclare LGPL 2.1 ou ultérieure ;
les [conditions FFmpeg](https://ffmpeg.org/legal.html) dépendent de sa construction.
Le package n’embarque ni ne distribue FFmpeg. Fournissez une installation adaptée
à votre système et vérifiez sa propre licence avant de la redistribuer.

Il faut le décodeur PNG, le démultiplexeur image2, l’encodeur natif `mpeg4`,
le multiplexeur MP4 et la conversion vers YUV420P. Une autre construction peut
échouer si ces capacités manquent ; l’échec et les diagnostics sont retournés.
L’application sonde d’abord `-version`, avec une limite de dix secondes.

## Images, dimensions et couleur

Pour N images à f Hz, les instants sont i/f, de 0 à N−1, et la durée vidéo
est N/f. La première pose a un delta nul. Pause, scopes, Animation et pas fixe
suivent la politique décrite dans le guide PNG. La cadence et le nombre
d’images doivent être strictement positifs ; la cadence entière est limitée à
65 535 Hz par la base de temps MPEG-4.

Les dimensions en pixels sont celles de la fenêtre après startup. Elles doivent
être paires et positives, puis rester fixes pendant la capture. Un changement
de dimensions est une erreur ; il ne produit pas une vidéo redimensionnée implicitement.

Le rendu final doit être opaque : le MP4 ne conserve pas le canal alpha.
La conversion RGBA vers YUV420P réduit la résolution des composantes de couleur
et le codec est avec perte. Utiliser le PNG pour les comparaisons exactes de pixels ;
les repères décodés de la vidéo se vérifient avec une tolérance adaptée.

## Disque et progression

Cette première voie conserve N PNG dans un dossier privé voisin de la sortie,
puis les encode automatiquement. Le besoin disque dépend donc du nombre et de
la complexité des images, en plus de la vidéo temporaire et de la copie finale.
Le moteur garde une seule capture en vol ; il n’accumule pas les images en mémoire.
Les buffers et ressources propres au processus FFmpeg s’ajoutent à cette mémoire.

Les événements restent pompés pendant le rendu, l’encodage et la publication.
La copie finale est exécutée par un job possédant ses ressources ; elle se termine
avant le retour. Ce parcours ne constitue pas encore un enregistrement temps réel.

## Erreurs et annulation

Un fichier existant est préservé, y compris s’il apparaît entre la préparation
et la publication. La destination est créée exclusivement et ses handles sont
fermés avant la réussite. Les diagnostics externes conservés sont limités à 16 Kio.

`application.stop()` ou une fermeture automatique de fenêtre annule l’export.
Pendant l’encodage, le processus est arrêté et récolté. Une publication déjà
acceptée est drainée puis sa destination est retirée si elle avait été créée
par cet export. Les PNG temporaires et la vidéo intermédiaire sont nettoyés.

Les erreurs de capture, d’encodeur, d’écriture ou de fermeture donnent un
`Result<int,str>` en échec. Une erreur de nettoyage indique le dossier restant ;
elle peut survenir après la création d’une vidéo déjà complète. Aucun fichier
inachevé n’est annoncé comme une réussite. La récupération après crash ou arrêt
forcé du processus n’est pas garantie.

[Revenir au rendu](README.md).
