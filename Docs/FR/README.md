# Composer un rendu avec GFX.Rendering

`GFX.Rendering` est un hôte de composition, pas le propriétaire des scènes.
Son `Renderer` expose le frame graph, les textures de sortie, l’enregistrement
des passes, le multisampling, les statistiques et la présentation à la fenêtre
active.

[Read this documentation in English.](../EN/README.md)

## Installer le package

```text
silex install GFX.Rendering
```

GFX.Rendering demande Silex 0.39.0 ou une version plus récente.

## Enregistrer et ordonner des passes

Une extension peut enregistrer ses passes, déclarer leurs dépendances et
retrouver ses propres ressources dans `Application` :

```sx
use GFX.Application
use GFX.GPU
use GFX.Rendering.Renderer

func draw(pass:@GPU.RenderPass, application:@Application) {
    // Retrieve the extension's private resources here.
}

var renderer = Renderer()
let scene = renderer.add_pass("Alternative.Scene", draw)
let overlay = renderer.add_pass("Alternative.Overlay", draw)
renderer.graph().depends(overlay, scene)
renderer.graph().require_compiled()
```

Les shaders appartiennent à l’extension qui définit la passe. Une passe avec
test de profondeur demande la cible partagée lors de son enregistrement :

```sx
renderer.add_pass("Alternative.Scene3D", draw, depth:true)
```

La texture de profondeur est aussi disponible par `depth_texture()` pour les
dépendances du frame graph. Les politiques de caméra, mesh, matériau et lumière
restent dans le domaine de scène ou l’extension.

Le [frame graph public](FrameGraph.md) peut également être construit et
inspecté sans le renderer générique.

## Choisir l’antialiasing

`Rendering.Plugin` emploie 4× MSAA par défaut sur les cibles couleur et
profondeur partagées. Si le device ne prend pas en charge les formats et le
nombre d’échantillons demandés, le rendu essaie successivement 8×, 4×, 2× puis
un seul échantillon.

Une application peut sélectionner une qualité avant d’installer sa scène :

```sx
application.add_plugin(Plugins.Rendering(
    Plugins.Rendering.Settings(
        antialiasing:Plugins.RenderingAntialiasing.msaa_8x,
    )
))
application.add_plugin(Plugins.Scene3D())
```

Ce fragment suppose une application et les catalogues GFX déjà importés.
`RenderingAntialiasing.none` sélectionne une cible mono-échantillon. Chaque
pipeline de la passe partagée doit employer le nombre effectivement résolu ;
les renderers Scene2D et Scene3D le configurent automatiquement.

MSAA lisse la couverture géométrique de la frame. Il ne filtre pas l’atlas
d’ombres séparé de Scene3D.

## Lire les statistiques de frame

`Rendering.Stats` rapporte le travail GPU soumis pour la frame terminée. Les
valeurs `draw_calls`, `triangles` et `instances` restent des totaux. Les
requêtes préfixées par `color_` séparent le rendu principal des requêtes
préfixées par `shadow_`, ce qui rend visible le coût des cascades d’ombres.

Le package contribue `Plugins.Rendering`, `Plugins.Rendering.Settings`,
`Plugins.RenderingAntialiasing` et `Resources.Renderer` aux catalogues ouverts
de GFX. La présentation reste synchronisée par défaut ; une mesure peut demander
explicitement `Rendering.PresentMode.immediate`.
