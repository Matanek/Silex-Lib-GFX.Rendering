# GFX.Rendering

`GFX.Rendering` provides GFX's generic rendering host: pass registration,
frame ordering, transient texture planning, multisampling, frame statistics,
and presentation to the active window. It deliberately owns no scene,
material, mesh, camera, or shader policy.

```sh
silex install GFX.Rendering
```

```silex
use GFX.Application
use GFX.GPU
use GFX.Rendering

func draw(pass:@GPU.RenderPass, application:@Application) {}

var renderer = Rendering.Renderer()
let scene = renderer.add_pass("Alternative.Scene", draw)
let overlay = renderer.add_pass("Alternative.Overlay", draw)
renderer.graph().depends(overlay, scene)
renderer.graph().require_compiled()
```

The frame graph remains an advanced public capability under
`GFX.Rendering.FrameGraph`; it belongs to the same package and release cycle as
the renderer that executes its plan. `GFX.Rendering` contributes
`Plugins.Rendering`, `Plugins.Rendering.Settings`,
`Plugins.RenderingAntialiasing`, and `Resources.Renderer` to GFX's open
catalogs.

Presentation remains synchronized by default. A latency or throughput
measurement can request immediate presentation explicitly without configuring
the lower-level GPU plugin itself:

```silex
application.add_plugin(Rendering.Plugin(Rendering.Plugin.Settings(
    present_mode:Rendering.PresentMode.immediate
)))
```

See [Docs/README.md](Docs/README.md) for renderer composition and
[Docs/FrameGraph.md](Docs/FrameGraph.md) for explicit graph construction.
