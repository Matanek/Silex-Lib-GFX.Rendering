# Construire un frame graph

`GFX.Rendering.FrameGraph` décrit les ressources logiques, les passes, leurs
accès et leurs dépendances. Le graphe est public : un renderer alternatif peut
le construire, le compiler, inspecter son plan et partager des ressources
transitoires dont les durées de vie ne se chevauchent pas.

```sx
use GFX.Rendering.FrameGraph

func main() {
    var graph = FrameGraph()
    let scene = graph.add_pass("Alternative.Scene")
    let overlay = graph.add_pass("Application.Overlay")
    graph.depends(overlay, scene)
    graph.require_compiled()
}
```

Les noms de passes expriment leur propriétaire logique. Une dépendance
explicite peut ordonner les passes de plusieurs extensions sans leur donner
accès aux ressources privées des autres.

[Revenir à la documentation Rendering](README.md)
