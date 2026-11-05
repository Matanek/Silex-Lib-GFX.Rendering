# Changelog

## [Unreleased]

- `Renderer.capture_png` saves the next complete render after MSAA resolution,
  with a ticket, cancellation, recoverable errors and exclusive output. Mapping,
  CPU copying, PNG encoding and writing use a dedicated worker; inactive capture
  performs no GPU readback. Offscreen alpha is preserved and presented output
  is opaque. Limits: one operation and 64 MiB of transfer storage per renderer.
