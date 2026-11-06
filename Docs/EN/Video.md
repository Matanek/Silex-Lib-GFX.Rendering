# Export an animation as MP4

`Rendering.export_mp4` exports a configured application as a silent video.
It preserves the controlled samples of [PNG export](Export.md), encodes them,
and finalizes the container before returning success. The initial format is
**MP4, MPEG-4 Part 2, YUV420P**, with fixed `q:v=2` quality and no B frames.
This is an offline path: computation time does not change the poses.

## Supply the encoder

FFmpeg is an external program explicitly selected by the consumer.
The function requires its **absolute path**, without PATH lookup, a shell,
or a runtime download. The output parent must exist and the final file
must be new.

After configuring the usual plugins and systems, this fragment replaces
`application.run()`:

```sx
match (try Rendering.export_mp4(
    application, "Animation.mp4", frames:60,
    ffmpeg:"/absolute/path/ffmpeg", frames_per_second:60
)) {
    failure(error) => { print(error) }
    success(count) => { print("Video complete: ", count, " frames") }
}
```

The optional `ready:(func(Application) bool)?` parameter follows the PNG
contract: preparation after startup, before time zero. The application must
not have run already. A compatible window and graphics session are still
required; a hidden window suits automated exports.

## Install a suitable FFmpeg

The qualification version is **FFmpeg 9.0.2**, built from the
[official sources](https://ffmpeg.org/download.html) with GPL, nonfree and
version3 components disabled. This binary declares LGPL 2.1 or later;
[FFmpeg's conditions](https://ffmpeg.org/legal.html) depend on its build.
The package neither bundles nor distributes FFmpeg. Supply an installation
for your system and check its own license before redistributing it.

The PNG decoder, image2 demuxer, native `mpeg4` encoder, MP4 muxer and
conversion to YUV420P are required. Another build may fail if these
capabilities are absent; errors and diagnostics are returned. The application
first probes `-version`, with a ten-second limit.

## Frames, dimensions and color

For N frames at f Hz, samples occur at i/f, from 0 to N−1, and video duration
is N/f. The first pose has zero delta. Pause, scopes, Animation and fixed
steps follow the policy in the PNG guide. Frame count and rate must be
strictly positive; integer frame rates are limited to 65,535 Hz by the
MPEG-4 time base.

Pixel dimensions are those of the window after startup. They must be
positive and even, then remain fixed during capture. A dimension change
is an error; it does not implicitly resize the video.

The final render must be opaque: MP4 does not preserve alpha. Conversion
from RGBA to YUV420P reduces color component resolution, and the codec is
lossy. Use PNG for exact pixel comparisons; decoded video markers require
an appropriate tolerance.

## Disk and progress

This initial path keeps N PNG files in a private directory next to the
output, then encodes them automatically. Disk usage therefore depends on
the number and complexity of frames, plus the temporary video and final
copy. The engine keeps one capture in flight; it does not accumulate frames
in memory. FFmpeg's own buffers and resources add to that memory.

Events keep being pumped during rendering, encoding and publication.
An owned job performs the final copy and completes before return.
This path serves offline export; [interactive recording](Recording.md) has its own driver.

## Errors and cancellation

An existing file is preserved, including one that appears between preparation
and publication. The destination is created exclusively and its handles are
closed before success. Retained external diagnostics are limited to 16 KiB.

`application.stop()` or automatic window closing cancels the export.
During encoding, the process is stopped and reaped. An accepted publication
is drained, then its destination is removed if this export created it.
Temporary PNG files and the intermediate video are cleaned up.

Capture, encoder, write or close errors return a failed `Result<int,str>`.
A cleanup error identifies the remaining directory; it can occur after a
complete video was created. An unfinished file is never reported as success.
Recovery after a crash or forced process termination is not guaranteed.

[Back to rendering](README.md).

To record a game in real time, use [interactive recording](Recording.md).
