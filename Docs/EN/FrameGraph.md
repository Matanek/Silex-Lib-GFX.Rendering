# Build a frame graph

`GFX.Rendering.FrameGraph` describes logical resources, passes, their access,
and their dependencies. The graph is public: an alternative renderer can build
and compile it, inspect its plan, and share transient resources whose lifetimes
do not overlap.

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

Pass names express their logical owner. An explicit dependency can order passes
from several extensions without granting access to each other's private
resources.

[Return to the Rendering documentation](README.md)
