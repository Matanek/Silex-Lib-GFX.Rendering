# Enregistrer une frame en PNG

La capture PNG conserve le prochain rendu complet de
`Rendering.Renderer`, après ses passes et la résolution du MSAA. Le PNG contient
les scènes et surimpressions composées dans ce renderer. Aucun accès au bureau,
aux décorations de fenêtre ni aux vues natives externes telles que WebView.

Dans un système Application, demander la capture puis garder son ticket :

```sx
var ticket = renderer.capture_png("scene.png")
```

Ce fragment suppose un `renderer:&Rendering.Renderer`. L'appel ordinaire arrête
le programme si la demande est refusée ; `try renderer.capture_png(path)` conserve
le `Result<Capture, str>` pour traiter un chemin invalide ou une capture déjà en
cours. Une seule capture peut être en attente par renderer. La capture vise le
prochain rendu après la demande, pas une image conservée de la frame précédente.

Lors des mises à jour suivantes, lire `ticket.state()` :

| État `Rendering.Capture.State` | Action |
| --- | --- |
| `pending` | Continuer l'application ; le renderer fait progresser l'opération. |
| `completed` | Le PNG est fermé et disponible à `ticket.path()`. |
| `failed` | Lire `ticket.error()` ; aucune réussite partielle n'est annoncée. |
| `cancelled` | L'annulation est terminée et la sortie de cette opération a été retirée. |

`ticket.cancel()` demande l'annulation. Une copie GPU déjà soumise peut finir,
mais n'est pas attendue par la boucle. Un job PNG déjà lancé termine avant
nettoyage de sa sortie ; le ticket reste `pending` jusque-là. Une erreur de
traitement ou de nettoyage reste `failed`. À la fermeture d'Application, les
captures pendantes sont annulées et les jobs acceptés sont drainés avant de
libérer le device. Une capture déjà terminée reste disponible.

## Dimensions, couleurs et fichiers

La capture emploie les dimensions physiques de la frame ; le redimensionnement
suivant ne les change pas. Les formats SDR RGBA8/BGRA8, unorm et sRGB, produisent
un PNG RGBA8 orienté haut/gauche. BGRA est réordonné, les octets sRGB restent
encodés. L'alpha est opaque en présentation et préservé en rendu hors écran
(`presentation:false`). HDR n'est pas pris en charge.

Le transfert est limité à 64 Mio, rangées alignées comprises. Une surface nulle,
indisponible, excessive ou de format non pris en charge fait échouer le ticket.
Le renderer inactif ne télécharge aucun pixel et ne lance aucun encodage. Lors
d'une capture, il utilise une cible intermédiaire et, en présentation, un blit.
La soumission reste dans le rendu ; mapping, copie CPU, encodage PNG et écriture
s'exécutent sur un worker dédié. Le coût GPU supplémentaire n'est pas nul.

Le chemin est relatif au répertoire d'exécution. Son parent doit exister ; aucun
fichier existant n'est écrasé. Les erreurs d'encodage, d'allocation de capture et
d'écriture sont signalées sur le ticket. Un fichier partiel créé par l'opération
est supprimé sur erreur ; un éventuel échec de nettoyage reste explicite dans
l'erreur. La perte du contexte de rendu demeure soumise au contrat GPU du moteur.

`silex run` lance le programme dans le dossier de son source : une sortie
`scene.png` s'y trouve donc aussi. Un exécutable lancé directement suit le
répertoire courant du lanceur. Le cache de compilation reste celui du workspace
depuis lequel la commande Silex est exécutée.

## Essayer le parcours complet

L'exemple public [RenderCapture.sx](https://github.com/Matanek/Silex-Examples/blob/main/Sources/RenderCapture.sx)
compose un cube 3D, du Canvas 2D et une interface UI. Dans le checkout de
développement dont les packages candidats sont liés, depuis `SilexProject/` :

```text
silex run Silex-Examples/Sources/RenderCapture.sx
```

Cliquer sur **Enregistrer PNG**, vérifier le retour visible puis ouvrir le fichier
annoncé. Le cube continue de tourner pendant le traitement. Un nouveau clic
emploie le nom suivant ; un nom existant provoque une erreur récupérable.

Les [tests consommateurs](../../Tests/Consumer/Tests/Capture.sx) rechargent les
PNG et vérifient pixels, dimensions, MSAA, resize et erreurs. Les
[tests de cycle de vie](../../Tests/Consumer/Tests/CaptureLifecycle.sx) couvrent
annulation et fermeture avec opérations en vol. Pour une suite d’images, suivre
[l’export à temps contrôlé](Export.md). Les guides [vidéo MP4](Video.md),
[enregistrement interactif](Recording.md) et [audio applicatif](Soundtrack.md)
présentent les parcours vidéo.
