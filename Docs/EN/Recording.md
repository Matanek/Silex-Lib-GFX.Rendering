# Record while the game keeps running

`Renderer.record_mp4` starts a silent video of the final composed render. The
game keeps its loop, input and real time during preparation, recording and
finalization. The [LiveRecording demo](https://github.com/Matanek/Silex-Examples/blob/main/Sources/LiveRecording.sx)
uses the button or **R** to start/stop, **A/D** or the arrow keys to move, and
**Escape** to quit.

## Start and keep the result

Provide a new output path and the **absolute FFmpeg path**, as for
[MP4 export](Video.md). The output parent must exist. The encoder must accept
RGBA `rawvideo` on stdin, convert to YUV420P and encode MPEG-4 Part 2 in MP4.
There is no shell, PATH lookup or download.

In a system with access to the renderer, this fragment starts a session:

```sx
match (try renderer.record_mp4("Partie.mp4", ffmpeg:"/chemin/absolu/ffmpeg", frames_per_second:30)) {
    success(recording) => { game.recording = recording }
    failure(error) => { print(error) }
}
```

Here, `game.recording` is a `Rendering.Recording?` field in the game. Keep this
handle to call `stop()`, `cancel()`, `state()`, `error()` and `statistics()`.
The renderer continues driving the session. One renderer accepts one unfinished
session; a still PNG remains available in parallel with its own bound.

`stop()` fixes the end of the recording period, then finalizes in the background.
Wait for `completed` before announcing the file or quitting the application.
States follow `preparing`, `recording`, `stopping`, then `completed`, `failed`
or `cancelled`. Stopping during preparation cancels the session.
`path()` retains the supplied path; `frames_per_second()` retains the rate.

## Real time and saturation

The integer rate ranges from 1 to 65,535 Hz; the default is 30 Hz. The period
starts after encoder preparation. The monotonic clock is independent of the
simulation delta, pause and render rate. The file contains `ceil(duration × rate)`
frames, with at least one frame: its rounded duration differs from the recorded
period by at most one video step. Stopping before the first completed image
returns a recoverable error.

A capture takes the render available at submission time. If the engine or encoder
falls behind, the last image is duplicated for missing instants. Before the first
capture, its first image fills that missing beginning. The engine then resumes
with a recent render; it neither queues every render nor speeds up playback to
catch up.

`statistics()` provides cumulative counters:

| Field | Meaning |
| --- | --- |
| `frames` | Images already sent to the encoder. |
| `captured` | GPU captures collected by the writer. |
| `duplicates` | Images sent by repeating a capture. |
| `dropped` | Elapsed video slots without a newly collected capture: `max(0, ceil(duration × rate) − captured)`. |
| `pending_images` | 0 or 1: a transfer or image job in progress. |
| `peak_pending_images` | Observed maximum of that count. |
| `duration_seconds` | Real time of the period, frozen by `stop()`. |

After success, `frames == captured + duplicates`. `dropped` counts slots without
a capture, not render frames: several renders may occur between two slots.
During finalization some counters keep advancing while the duration stays fixed.

## Resources and limits

The queue holds **one GPU transfer or image job**, plus the last CPU image.
During a job the new CPU image adds to that last image. Buffers remain bounded
by the dimensions; there is no temporary PNG sequence. The transfer limit is
64 MiB, including aligned pitch, as for PNG. The resolved render, encoder buffers
and video on disk add to this memory.

The renderer observes the fence without waiting. A dedicated worker maps the
ready transfer, copies/normalizes pixels and writes the pipe; it does not occupy
the Application systems pool. GPU submission, readiness checks, process tracking
and orchestration remain costs of the main render path. Inactive capture starts
no GPU download or encoder. Cost depends on hardware, resolution and the Silex
build; no minimum frame rate is guaranteed.

Physical dimensions must be positive, even and fixed. Resizing during the
recording period fails this session while leaving the game running. MP4 uses
lossy MPEG-4 Part 2/YUV420P, `q:v=2`, no B frames and no alpha channel. Presented
content is opaque; an offscreen target must also be rendered opaque for the
expected composition.

## Cancel, quit and handle errors

`cancel()` discards the video and terminates the encoder. Application shutdown
does the same for an active or finalizing session. Accepted jobs are drained
before closing their resources. FFmpeg preparation has a ten-second limit;
cancellation can therefore stay in `stopping` until the probe returns. This
wait does not block frames, but application shutdown can wait for preparation.

An image write and encoder finalization each have a ten-second limit observed
by the renderer; expiry terminates the encoder and returns a recoverable failure.
The supplied program must be a trusted FFmpeg: the driver controls that process,
not an arbitrary family of descendants.

Retained diagnostics are limited to 16 KiB. An existing destination, including
one created during recording, is preserved. Publication creates the file
exclusively and finishes copying before `completed`. Cancellation or failure
removes only a destination created by this session. The private sibling directory
and intermediate movie are cleaned up; a cleanup error reports what remains.
Recovery after a crash or forced game termination is not guaranteed.

The public path and its errors run locally on macOS ARM64. Composition and link
checks on other targets do not prove native execution of their STD adapters
or their FFmpeg builds.

[Back to rendering](README.md).
