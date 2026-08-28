# Compose rendering with GFX.Rendering

`GFX.Rendering` is a composition host, not the owner of scenes. Its `Renderer`
exposes the frame graph, output textures, pass registration, multisampling,
statistics, and presentation to the active window.

[Lire cette documentation en français.](../FR/README.md)

## Install the package

```text
silex install GFX.Rendering
```

GFX.Rendering requires Silex 0.39.0 or newer.

## Register and order passes

An extension can register its passes, declare their dependencies, and retrieve
its own resources from `Application`:

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

Shaders belong to the extension that defines the pass. A pass with depth
testing requests the shared target when it is registered:

```sx
renderer.add_pass("Alternative.Scene3D", draw, depth:true)
```

The depth texture is also available through `depth_texture()` for frame-graph
dependencies. Camera, mesh, material, and lighting policy remain in the scene
domain or extension.

The [public frame graph](FrameGraph.md) can also be built and inspected without
the generic renderer.

## Choose antialiasing

`Rendering.Plugin` uses 4× MSAA by default on the shared color and depth
targets. If the device cannot use the requested formats and sample count,
rendering tries 8×, 4×, 2×, then a single sample.

An application can select a quality before installing its scene:

```sx
application.add_plugin(Plugins.Rendering(
    Plugins.Rendering.Settings(
        antialiasing:Plugins.RenderingAntialiasing.msaa_8x,
    )
))
application.add_plugin(Plugins.Scene3D())
```

This fragment assumes an application and imported GFX catalogs.
`RenderingAntialiasing.none` selects a single-sample target. Every pipeline in
the shared pass must use the resolved count; the Scene2D and Scene3D renderers
configure it automatically.

MSAA smooths frame-target geometry coverage. It does not filter Scene3D's
separate shadow atlas.

## Read frame statistics

`Rendering.Stats` reports GPU work submitted for the completed frame. The
`draw_calls`, `triangles`, and `instances` values remain totals. Queries
prefixed with `color_` separate main rendering from those prefixed with
`shadow_`, making cascaded-shadow cost visible.

The package contributes `Plugins.Rendering`, `Plugins.Rendering.Settings`,
`Plugins.RenderingAntialiasing`, and `Resources.Renderer` to GFX's open
catalogs. Presentation remains synchronized by default; a measurement can
request `Rendering.PresentMode.immediate` explicitly.
