# Exporter une vidéo avec le son de l’application

`Rendering.export_mp4` peut inclure le mix d’un `Audio.offline`. L’exporteur
rend les images et le son sur la même chronologie, puis produit un MP4 avec
vidéo MPEG-4 Part 2 et audio AAC stéréo ou mono avec un débit cible de 192 kbit/s. Le temps de calcul
peut dépasser la durée du film sans modifier sa vitesse ni perdre ses images.

[Exemple complet VideoWithAudio](https://github.com/Matanek/Silex-Examples/blob/main/Sources/VideoWithAudio.sx) :
un cube animé, un marqueur qui clignote et un bip toutes les demi-secondes,
pendant quatre secondes à 60 images/s.

## Choisir le mix

Ce fragment s’ajoute à une application configurée avec ses systèmes et plugins :

```sx
var audio = Audio.offline(sample_rate:48_000, channels:2)
match (try Rendering.export_mp4(
    application, "Animation-Audio.mp4", frames:240,
    ffmpeg:"/chemin/absolu/ffmpeg", frames_per_second:60, audio:audio
)) {
    success(count) => { print("Vidéo avec son terminée : ", count, " images") }
    failure(error) => { print(error) }
}
```

Importer `GFX.Audio` et `GFX.Rendering`. Le mix choisi est installé comme ressource
`Audio` avant startup, en remplaçant cette ressource si elle existait. Les systèmes
ordinaires recevant `audio:&Audio` peuvent préparer, jouer, arrêter et modifier
les sons. Le plugin Audio réutilise cette ressource s’il est présent. Les autres
instances Audio possédées par l’application ne sont pas enregistrées.

Un mix avec périphérique est rejeté avant d’ouvrir une fenêtre ou une sortie.
Le rendu hors ligne n’a besoin d’aucun périphérique audio. Il consomme l’état
courant du mix, sans le rembobiner ; les attentes de chargement via `ready` ne
le font pas avancer. Manipuler ce mix depuis les systèmes contrôlés uniquement,
sans accès concurrent depuis un autre thread ou un callback natif pendant sa
collecte. L’exporteur garde sa référence jusqu’au retour.

Le paramètre `audio` est optionnel : les appels existants restent muets. Le
parcours [d’enregistrement au temps réel](Recording.md) est encore muet ; cette
option qualifie uniquement l’export contrôlé.

## Chronologie et fin

L’image i est prise à i/f après les systèmes contrôlés. Le mix est ensuite rendu
pour l’intervalle [i/f, (i+1)/f[. Les commandes émises par ces systèmes prennent
effet à leur instant échantillonné. Les commandes d’une timeline audio interne
peuvent conserver une précision plus fine selon le contrat de GFX.Audio.

Le nombre de frames audio à la frontière k est `floor(k × fréquence / f)`.
L’arrondi est cumulé, même lorsque la fréquence audio n’est pas divisible par
la cadence vidéo. La durée du mix couvre donc la période vidéo à moins d’une
frame audio près. Le delta initial de simulation est nul, mais le premier
intervalle audio est bien produit.

La pause d’une animation ou de la simulation suit leur contrat existant ; elle
ne met pas automatiquement en pause les lectures Audio. Utiliser les commandes
Audio de pause/reprise pour obtenir cette pause sonore. Après la fin des sons,
le mix rend du silence. Les réverbérations et fins de notes dépassant la durée
demandée ne prolongent pas automatiquement la vidéo : prévoir assez de frames
pour les conserver.

AAC est avec perte et introduit un délai d’encodage ainsi qu’un remplissage de
fin par blocs. L’export utilise les informations temporelles du conteneur ; une
vérification des samples décodés doit respecter sa durée valide et les indications
de délai/remplissage. Les comparaisons audio exactes utilisent le PCM de référence,
pas une égalité binaire entre samples AAC décodés.

## Encodeur, ressources et erreurs

Fournir un FFmpeg explicite comme pour [la vidéo muette](Video.md), avec entrée
`f32le`, conversion audio, encodeur natif `aac` et multiplexeur MP4 disponibles.
La qualification utilise 44 100 et 48 000 Hz, mono/stéréo ; les autres fréquences
peuvent être refusées par l’encodeur et donnent une erreur récupérable. Aucun
codec supplémentaire n’est téléchargé ni installé à l’exécution.

Le moteur garde au plus un bloc de rendu audio de 4 096 frames à la fois,
avec ses samples float32, leurs octets et le buffer natif temporaire. À 48 kHz
stéréo, le PCM temporaire sur disque croît de 384 000 octets par seconde, en plus
des PNG et de la vidéo intermédiaire décrits dans le guide MP4. Les sons,
convertisseurs et buffers propres à l’application et à FFmpeg s’ajoutent à ces
ressources ; aucune mémoire ou cadence universelle n’est promise.

Un worker dédié rend le mix, écrit, ferme et synchronise son fichier temporaire.
L’exporteur pompe les événements pendant ses travaux et n’exécute pas un nouveau
pas de simulation avant la fin de l’échantillon. Il finalise les deux pistes et
publie exclusivement la destination avant la réussite. Annulation, erreur de
rendu, d’écriture ou d’encodage nettoient aussi le PCM temporaire ; un échec de
nettoyage rapporte ce qui reste. Le mix déjà consommé n’est pas restauré après
un échec. Les protections de sortie et limites de crash du guide MP4 s’appliquent.

Le package nécessite Silex 0.47.1 et dépend de GFX.Audio pour ce parcours. Les
constructions et liaisons non hôtes sont distinguées des exécutions natives.
Webcam, microphone et capture audio du système ne font pas partie de cet export.

[Revenir au rendu](README.md).
