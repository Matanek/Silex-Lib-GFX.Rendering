# Save a frame as PNG

PNG capture saves the next complete `Rendering.Renderer`
render, after its passes and MSAA resolution. The PNG includes scenes and
overlays composed in that renderer. It does not access the desktop, window
decorations or external native views such as WebView.

In an Application system, request a capture and retain its ticket:

```sx
var ticket = renderer.capture_png("scene.png")
```

This fragment assumes a `renderer:&Rendering.Renderer`. An ordinary call stops
the program if the request is rejected; `try renderer.capture_png(path)` keeps
the `Result<Capture, str>` to handle an invalid path or an already pending
capture. Only one capture can be pending per renderer. The request targets the
next render, not a retained image from the previous frame.

On subsequent updates, read `ticket.state()`:

| `Rendering.Capture.State` | Action |
| --- | --- |
| `pending` | Continue the application; the renderer advances the operation. |
| `completed` | The PNG is closed and available at `ticket.path()`. |
| `failed` | Read `ticket.error()`; partial work is never reported as success. |
| `cancelled` | Cancellation finished and this operation's output was removed. |

`ticket.cancel()` requests cancellation. An already submitted GPU copy can
finish, but the loop does not wait for it. An already dispatched PNG job finishes
before its output is cleaned up; the ticket stays `pending` until then. Processing
or cleanup errors remain `failed`. On Application shutdown, pending captures are
cancelled and accepted jobs are drained before releasing the device. Completed
captures remain available.

## Dimensions, colors and files

Capture uses the frame's physical pixel dimensions; later resizing does not
change them. SDR RGBA8/BGRA8 unorm and sRGB formats produce a top-left-oriented
RGBA8 PNG. BGRA is reordered and sRGB bytes stay encoded. Alpha is opaque when
presenting and preserved offscreen (`presentation:false`). HDR is unsupported.

Transfer storage is limited to 64 MiB, including aligned rows. An empty,
unavailable, oversized or unsupported surface fails the ticket. When inactive,
the renderer downloads no pixels and starts no encoding. Capture uses an
intermediate target and, when presenting, a blit. Submission stays in rendering;
mapping, CPU copying, PNG encoding and writing run on a dedicated worker. The
additional GPU work has a nonzero cost.

The path is relative to the execution directory. Its parent must exist;
existing files are never overwritten. Encoding, capture allocation and write
errors are reported on the ticket. Partial files created by the operation are
removed on error; a cleanup failure is included in the error. Loss of the render
context remains subject to the engine's GPU contract.

`silex run` starts the program in its source directory, so `scene.png` is written
there too. A directly launched executable follows its launcher's current working
directory. The compilation cache still belongs to the workspace from which the
Silex command runs.

## Try the complete workflow

The public [RenderCapture.sx](https://github.com/Matanek/Silex-Examples/blob/main/Sources/RenderCapture.sx)
example combines a 3D cube, 2D Canvas drawing and a UI. In a development checkout
with the candidate packages linked, run from `SilexProject/`:

```text
silex run Silex-Examples/Sources/RenderCapture.sx
```

Click **Enregistrer PNG**, check the visible feedback and open the reported
file. The cube keeps rotating during processing. Another click uses the next
name; an existing name causes a recoverable error.

The [consumer tests](../../Tests/Consumer/Tests/Capture.sx) reload PNGs and check
pixels, dimensions, MSAA, resizing and errors. The
[lifecycle tests](../../Tests/Consumer/Tests/CaptureLifecycle.sx) cover cancellation
and shutdown with work in flight. For an image sequence, follow
[controlled export](Export.md). The [MP4 video](Video.md),
[interactive recording](Recording.md) and [application audio](Soundtrack.md)
guides describe the video workflows.
