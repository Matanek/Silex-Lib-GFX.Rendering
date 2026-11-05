# Export an animation as PNG frames

`Rendering.export_png` produces a complete sequence at a chosen frame rate:
60 images at 60 Hz represent one second, regardless of computation or write
time. Export waits for each PNG before advancing the simulation.

The [AnimationExport example](https://github.com/Matanek/Silex-Examples/blob/main/Sources/AnimationExport.sx)
combines an animated cube, a 2D drawing and a user interface. It writes
`frame-000000.png` through `frame-000059.png`, then prints the absolute directory.
The [verification consumer](../../Tests/Consumer/Tests/Export.sx)
also checks every pixel of a simple scene.

## Export a configured application

This fragment replaces `application.run()` after the usual plugin and system
configuration:

```sx
match (try Rendering.export_png(application, "Frames", frames:60, frames_per_second:60)) {
    failure(error) => { print(error) }
    success(count) => { print("Images written: ", count) }
}
```

The directory must be new and its parent must exist. It is created before
startup; an existing directory is rejected, even when empty. Files remain
exclusive if another writer intervenes later. Success returns the number of
completed PNG files. Export owns this application's loop, which must not have
run before; it does not invoke a custom runner.

## Prepare before time zero

The optional `ready:(func(Application) bool)?` callback runs after `initialize`
and `startup`, before any simulation. It may collect loading work and returns
`true` when the required resources are ready. While waiting, events are pumped;
no simulation system is repeated and `FrameTime.delta` stays zero. The predicate
may stop the application to cancel preparation. It must return promptly and
report errors belonging to its own resources.

The [preparation test](../../Tests/Consumer/Tests/ExportPreparation.sx)
loads an actual PNG on a worker, waits for it and uses it in the first image.
Loading time does not shift the initial pose.

## Simulation time and pause

For N images at rate f, samples are indexed from 0 through N−1 at times i/f,
for an output duration of N/f. The first step has zero delta; subsequent steps
have a delta of 1/f. The order is `pre_update`, `update`, `post_update`, `render`,
then PNG completion before the next step. The last pose of 60 images at 60 Hz
is therefore the pose at 59/60 s.

`FrameTime`, `Simulation` and child scopes receive the controlled-time policy.
Animation and Physics use it normally; all due fixed physics steps finish before
rendering, without the realtime catch-up limit. A simulation pause produces
repeated poses without stopping frame numbering; `always` systems retain their
usual policy. Wall clocks from `STD.Time.Clock`, input and random seeds remain
the scene's responsibility.
Systems must not override `FrameTime.delta` themselves during this export.

Deltas and graphical consumers use the engine's current floating-point types:
small rounding differences are possible. Qualified repeatability concerns the
same scene and environment, not universal binary identity across GPUs. Flat test
markers compare exactly; numeric poses have an explicit tolerance.

## Waiting, errors and stopping

Capture keeps at most one image in flight and retains its 64 MiB PNG transfer
limit. Waiting advances GPU and encoding work without repeating render passes
or simulation; window events are still handled.
This offline export may take longer than its output duration; it
does not produce a video file.

`application.stop()` cancels export. Closing completes the application lifecycle
and cancels or drains the current write according to the [PNG capture](Capture.md)
contract. Completed PNG files remain available. A failure never becomes success:
the message reports how many frames completed. Preparation that never becomes
ready must supply its own stop condition.

The path currently uses a window and a graphical session supported by the renderer.
`presentation:false` avoids presenting each image; a hidden window supports
automated exports. This does not guarantee operation without a display server.
No audio or desktop capture is included.

[Return to rendering](README.md).
