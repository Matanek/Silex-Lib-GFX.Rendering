# GFX.Rendering

`GFX.Rendering` is a composition host, not the owner of scenes. Its `Renderer`
exposes the `FrameGraph`, output texture, and pass registration. A third-party
extension can register a pass, declare its dependencies, and retrieve its own
resources from `Application`.

```silex
use GFX.Application
use GFX.GPU
use GFX.Rendering.Renderer

func draw(pass:@GPU.RenderPass, application:@Application) {
    // The pass retrieves its extension's private resources here.
}

var renderer = Renderer()
let scene = renderer.add_pass("Alternative.Scene", draw)
let overlay = renderer.add_pass("Alternative.Overlay", draw)
renderer.graph().depends(overlay, scene)
renderer.graph().require_compiled()
```

Custom shaders belong to the extension that defines the pass:

```silex
let program = GPU.ShaderProgram.hlsl(file:"Shaders/Scene.hlsl")
```

This extension requires no non-public access to `GFX.Rendering`.

The frame graph is distributed with Rendering and remains available as the
advanced `GFX.Rendering.FrameGraph` module. See [FrameGraph.md](FrameGraph.md)
for standalone construction and plan inspection.

A pass that performs depth testing requests the shared frame depth target when
it is registered:

```silex
renderer.add_pass("Alternative.Scene3D", draw, depth:true)
```

The depth texture is also exposed by `depth_texture()` for frame-graph
dependencies. Camera, mesh, material, and lighting policy still belong to the
scene domain or to the extension, never to `GFX.Rendering`.

## Multisample antialiasing

`Rendering.Plugin` uses 4× MSAA by default for the shared color and depth
targets. If a device cannot render the selected formats at the requested sample
count, rendering falls back from 8× to 4×, then 2× and finally one sample.
Applications can select another quality level before installing a scene plugin:

```silex
application.add_plugin(Plugins.Rendering(
    Plugins.Rendering.Settings(
        antialiasing:Plugins.RenderingAntialiasing.msaa_8x
    )
))
application.add_plugin(Plugins.Scene3D())
```

Use `RenderingAntialiasing.none` for a single-sample target. Every pipeline
registered into the shared render pass must use the active sample count; the
built-in Scene2D and Scene3D renderers configure this automatically. A scene
package can read that resolved value through `Renderer.sample_count()` when it
creates its pipelines, without depending on Rendering's private MSAA resource.

MSAA smooths geometry coverage at the frame target. It does not filter the
separate Scene3D shadow atlas; sun-shadow filtering and cascades remain a
Scene3D concern.

## Frame statistics

`Rendering.Stats` reports submitted GPU work for the completed frame. Existing
`draw_calls`, `triangles`, and `instances` values remain totals. The
`color_draw_calls`, `color_triangles`, and `color_instances` queries separate
the main rendering work from `shadow_draw_calls`, `shadow_triangles`, and
`shadow_instances`. This distinction makes cascaded shadow cost visible even
when every cascade shares one atlas render pass.
