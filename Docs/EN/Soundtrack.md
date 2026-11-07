# Export a video with application audio

`Rendering.export_mp4` can include the mix of an `Audio.offline`. The exporter
renders images and audio on the same timeline, then produces MP4 with MPEG-4
Part 2 video and mono or stereo AAC targeting 192 kbit/s. Computation may take longer
than the movie without changing playback speed or dropping images.

[Complete VideoWithAudio example](https://github.com/Matanek/Silex-Examples/blob/main/Sources/VideoWithAudio.sx):
an animated cube, a flashing marker and a beep every half-second, for four
seconds at 60 frames/s.

## Choose the mix

Add this fragment to an application configured with its systems and plugins:

```sx
var audio = Audio.offline(sample_rate:48_000, channels:2)
match (try Rendering.export_mp4(
    application, "Animation-Audio.mp4", frames:240,
    ffmpeg:"/absolute/path/to/ffmpeg", frames_per_second:60, audio:audio
)) {
    success(count) => { print("Video with audio completed: ", count, " frames") }
    failure(error) => { print(error) }
}
```

Import `GFX.Audio` and `GFX.Rendering`. The selected mix is installed as the
`Audio` resource before startup, replacing that resource if it existed. Ordinary
systems receiving `audio:&Audio` can prepare, play, stop and modify sounds. The
Audio plugin reuses this resource if present. Other Audio instances owned by
the application are not recorded.

A device-backed mix is rejected before opening a window or output. Offline
rendering requires no audio device. It consumes the mix's current state without
rewinding it; loading waits through `ready` do not advance it. Manipulate this
mix only from controlled systems, without concurrent access from another thread
or native callback during collection. The exporter keeps its reference until
return.

The `audio` parameter is optional: existing calls remain silent.
To [record in real time with audio](Recording.md), pass a device mix to
`Renderer.record_mp4(..., audio:audio)`. The offline mix in this guide serves
controlled export.

## Timeline and ending

Image i is captured at i/f after controlled systems. The mix is then rendered
for interval [i/f, (i+1)/f[. Commands issued by these systems take effect at their
sampled instant. Commands in an internal audio timeline may retain finer
precision according to the GFX.Audio contract.

The audio frame count at boundary k is `floor(k × sample rate / f)`. Rounding
is cumulative, including when the sample rate is not divisible by the video
rate. The mix therefore covers the video period to within one audio frame.
The initial simulation delta is zero, but the first audio interval is produced.

Animation or simulation pause follows its existing contract; it does not
automatically pause Audio playback. Use Audio pause/resume commands for that
sound pause. The mix renders silence after sounds finish. Reverb and note tails
beyond the requested duration do not automatically extend the video: request
enough frames to keep them.

AAC is lossy and introduces encoder delay and block padding at the end. Export
uses container timing information; checking decoded samples must respect the
valid duration and delay/padding information. Exact audio comparisons use the
reference PCM, not binary equality between decoded AAC samples.

## Encoder, resources and errors

Supply an explicit FFmpeg as for [silent video](Video.md), with `f32le` input,
audio conversion, the native `aac` encoder and MP4 muxer available. Qualification
uses 44,100 and 48,000 Hz, mono/stereo; other rates may be rejected by the encoder
and return a recoverable error. No additional codec is downloaded or installed
at runtime.

The engine keeps at most one audio render block of 4,096 frames at a time, with
its float32 samples, their bytes and temporary native buffer. At 48 kHz stereo,
staged PCM disk use grows by 384,000 bytes per second, in addition to the PNGs
and intermediate video described in the MP4 guide. Application sounds,
converters and FFmpeg buffers add to these resources; no universal memory or
frame-rate guarantee is made.

A dedicated worker renders the mix, writes, closes and flushes its temporary
file. The exporter pumps events during that work and does not run another
simulation step before the sample completes. It finalizes both tracks and
publishes the destination exclusively before success. Cancellation, rendering,
write or encoding failure also clean up temporary PCM; cleanup failure reports
what remains. An already-consumed mix is not restored after failure. The MP4
guide's output protections and crash limits apply.

The package requires Silex 0.47.1 and depends on GFX.Audio for this path.
Non-host composition/link checks are distinguished from native execution.
Webcam, microphone and system audio capture are outside this export.

[Back to rendering](README.md).
