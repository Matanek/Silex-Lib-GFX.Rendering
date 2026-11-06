# Enregistrer pendant que le jeu continue

`Renderer.record_mp4` démarre une vidéo sans son du rendu final composé. Le jeu
conserve sa boucle, ses entrées et son temps réel pendant la préparation,
l’enregistrement et la finalisation. La [démo LiveRecording](https://github.com/Matanek/Silex-Examples/blob/main/Sources/LiveRecording.sx)
propose le bouton ou **R** pour démarrer/arrêter, **A/D** ou les flèches pour
bouger et **Échap** pour quitter.

## Démarrer et conserver le résultat

Fournir un chemin de sortie nouveau et le **chemin absolu de FFmpeg**, comme pour
l’[export MP4](Video.md). Le parent de la sortie doit exister. L’encodeur doit
accepter `rawvideo` RGBA sur stdin, convertir vers YUV420P et encoder MPEG-4 Part 2
dans MP4. Aucun shell, recherche PATH ou téléchargement n’intervient.

Dans un système disposant du renderer, ce fragment démarre une session :

```sx
match (try renderer.record_mp4("Partie.mp4", ffmpeg:"/chemin/absolu/ffmpeg", frames_per_second:30)) {
    success(recording) => { game.recording = recording }
    failure(error) => { print(error) }
}
```

`game.recording` désigne ici un champ `Rendering.Recording?` du jeu. Garder ce
handle pour appeler `stop()`, `cancel()`, `state()`, `error()` et `statistics()`.
Le renderer continue à piloter la session. Un renderer accepte une seule session
non terminée ; le PNG ponctuel reste utilisable en parallèle avec sa propre borne.

`stop()` fixe la fin de la période enregistrée, puis finalise en arrière-plan.
Attendre `completed` avant d’annoncer le fichier ou de quitter l’application.
Les états suivent `preparing`, `recording`, `stopping`, puis `completed`, `failed`
ou `cancelled`. Une session arrêtée pendant sa préparation est annulée.
`path()` conserve le chemin fourni ; `frames_per_second()` conserve la cadence.

## Temps réel et saturation

La cadence entière est comprise entre 1 et 65 535 Hz ; 30 Hz est la valeur par
défaut. La période commence après préparation de l’encodeur. L’horloge monotone
est indépendante du delta de simulation, de la pause et du rythme des rendus.
Le fichier contient `ceil(durée × cadence)` images, avec au moins une image :
sa durée arrondie diffère donc de la période enregistrée d’au plus un pas vidéo.
Un arrêt avant la première image achevée donne une erreur récupérable.

Une capture prend le rendu disponible à son instant de soumission. Si le moteur
ou l’encodeur prend du retard, la dernière image est dupliquée pour les instants
manquants. Avant la première capture, sa première image remplit ce début manquant.
Le moteur reprend ensuite avec un rendu récent ; il ne met pas tous les rendus
en file et n’accélère pas la lecture pour rattraper le retard.

`statistics()` fournit des compteurs cumulés :

| Champ | Signification |
| --- | --- |
| `frames` | Images déjà transmises à l’encodeur. |
| `captured` | Captures GPU collectées par le writer. |
| `duplicates` | Images transmises en répétant une capture. |
| `dropped` | Créneaux vidéo écoulés sans nouvelle capture collectée : `max(0, ceil(durée × cadence) − captured)`. |
| `pending_images` | 0 ou 1 : un transfert ou un job d’image en cours. |
| `peak_pending_images` | Maximum observé de ce nombre. |
| `duration_seconds` | Temps réel de la période, figé par `stop()`. |

Après réussite, `frames == captured + duplicates`. `dropped` mesure les créneaux
sans capture, pas le nombre de frames de rendu : plusieurs rendus peuvent se
produire entre deux créneaux. Pendant la finalisation, certains compteurs
continuent d’avancer alors que la durée reste figée.

## Ressources et limites

La file garde **un transfert GPU ou un job d’image**, ainsi que la dernière image
CPU. Pendant un job, la nouvelle image CPU s’ajoute à cette dernière. Les buffers
restent bornés par les dimensions ; il n’y a pas de séquence PNG temporaire.
La limite de transfert est 64 Mio, avec un pitch aligné, comme pour le PNG.
Le rendu résolu, les buffers de l’encodeur et la vidéo sur disque s’y ajoutent.

Le renderer observe la fence sans attendre. Un worker dédié mappe le transfert
prêt, copie/normalise les pixels et écrit le pipe ; il ne monopolise pas le pool
des systèmes Application. La soumission GPU, la vérification de disponibilité,
le suivi du processus et l’orchestration restent des coûts du rendu principal.
La capture inactive ne déclenche aucun téléchargement GPU ni encodeur.
Le coût dépend du matériel, de la résolution et de la construction Silex : aucune
cadence minimale n’est garantie.

Les dimensions physiques doivent être paires, positives et fixes. Redimensionner
pendant la période enregistrée fait échouer cette session, tout en laissant le
jeu continuer. Le MP4 utilise MPEG-4 Part 2/YUV420P avec perte, `q:v=2`, sans images B
et sans canal alpha. Le contenu présenté est opaque ; une cible hors écran doit
elle aussi être rendue opaque pour obtenir la composition attendue.

## Annuler, quitter et gérer une erreur

`cancel()` abandonne la vidéo et termine l’encodeur. La fermeture de l’application
fait de même pour une session encore active ou en finalisation. Les jobs déjà
acceptés sont drainés avant de fermer leurs ressources. La préparation de FFmpeg
a une limite de dix secondes ; son annulation peut donc rester en `stopping`
jusqu’au retour de la sonde. Cette attente ne bloque pas les frames, mais une
fermeture de l’application peut attendre la fin de cette préparation.

Une écriture d’image et la finalisation de l’encodeur ont chacune une limite de
dix secondes, observée par le renderer ; un dépassement termine l’encodeur et
rend l’échec récupérable. Un programme fourni doit être un FFmpeg de confiance :
le pilote contrôle ce processus, pas une famille arbitraire de descendants.

Les diagnostics conservés sont limités à 16 Kio. Une destination existante, y
compris créée pendant l’enregistrement, est préservée. La publication crée le
fichier exclusivement et termine sa copie avant `completed`. Une annulation ou
une erreur retire uniquement la destination créée par cette session. Le dossier
privé voisin et la vidéo intermédiaire sont nettoyés ; une erreur de nettoyage
indique ce qui reste. La récupération après crash ou arrêt forcé du jeu n’est
pas garantie.

Le parcours public et ses erreurs sont exécutés localement sur macOS ARM64.
Les compositions et liaisons des autres cibles ne constituent pas une preuve
d’exécution native de leurs adaptateurs STD ou de leur FFmpeg.

[Revenir au rendu](README.md).
