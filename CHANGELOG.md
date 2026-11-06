# Changelog

## [Unreleased]

- `Renderer.record_mp4` records the composed render while playing: owned session, asynchronous stop/finalization, bounded queue, real duration with duplication and counters, cancellation and recoverable errors. FFmpeg remains explicit; inactive capture performs no transfer.

- `export_mp4` produces a silent video at controlled times with an explicitly selected FFmpeg: MP4/MPEG-4 Part 2/YUV420P, temporary PNG sequence, exclusive output, cancellation and cleanup.

- `export_png` produces an indexed sequence at controlled times, waits for preparation before t=0 and preserves completed PNG files on stopping or failure.

- `Renderer.capture_png` saves the next complete render after MSAA resolution,
  with a ticket, cancellation, recoverable errors and exclusive output. Mapping,
  CPU copying, PNG encoding and writing use a dedicated worker; inactive capture
  performs no GPU readback. Offscreen alpha is preserved and presented output
  is opaque. Limits: one operation and 64 MiB of transfer storage per renderer.
