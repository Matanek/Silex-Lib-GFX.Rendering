# Qualify interactive recording

Run all Silex commands from the `SilexProject` workspace root, or the owning Spec
worktree group. Use the candidate compiler and workspace links. A functioning
graphics session and a qualified FFmpeg executable are required for native runs.

The ordinary `silex test Packages/GFX.Rendering/Tests` suite covers validation,
one active session, pre-start cancellation, and the existing PNG/export paths.
The standalone programs below cross asynchronous stages without timing-based
performance assertions:

```sh
silex compile Packages/GFX.Rendering/Tests/Consumer/Smokes/LiveRecording.sx --debug -o .silex/recording-consumer
.silex/recording-consumer /absolute/path/to/ffmpeg /new/output.mp4 normal

silex compile Packages/GFX.Rendering/Tests/Smokes/RecordingProgress.sx --debug -o .silex/recording-progress
.silex/recording-progress complete /absolute/path/to/ffmpeg /new/held.mp4
```

Consumer modes include `normal`, `short`, `cancel`, `cancel-prepare`, `shutdown`,
`resize`, `odd`, `encoder-error`, `conflict` and `conflict-late`. Supply an existing
output only for `conflict` and verify its bytes remain unchanged. `conflict-late`
creates a competing output after preparation; verify its text is preserved.
Every other run requires a distinct new output. Failed/cancelled runs assert
that no final output exists.

`RecordingProgress` delays observing a real owned GPU transfer for 60 render
progress calls. It does not make the GPU artificially slow or occupy a worker.
The `complete` mode checks duplicate backfill, input snapshots and continued
renders. `cancel` cancels that held transfer; `early-stop` stops before its first
image; `cancel-publication` cancels an accepted publication job and checks that
it reaches a terminal cancelled state. Verify no final file or sibling workspace
remains for those three modes.

The native input proof belongs to GFX, which owns SDL event injection:

```sh
silex compile Packages/GFX/Tests/Smokes/LiveRecording.sx --release -o .silex/recording-native
.silex/recording-native normal /absolute/path/to/ffmpeg /new/native.mp4 /new/unused-marker
```

This smoke uses one Application worker and verifies an independent typed heartbeat system every frame. It injects alternating native key events,
checks input delivery and emits `SAMPLE` rows and a final `RESULT`. `variable` alternates 90 Hz and 12 Hz frame periods; `idle` checks
zero GPU downloads; `blocked` and `shutdown` wait for a fixture PID marker before
injecting input, then cancel or close after 90 more frames. `probe-cancel` cancels
a deliberately stalled version probe. Native writes and worker thread identity
are additionally covered by STD's `Tests/SubprocessWriter.sx`.

## Encoder fixtures

`Tools/RecordingEncoder.py` is test tooling, never part of the runtime package.
Create an executable copy with an absolute Python shebang because the recording
process inherits no environment. Place JSON at `<launcher>.json`, for example:

```json
{"mode":"blocked","marker":"/absolute/path/to/marker.pid","ffmpeg":"/absolute/path/to/ffmpeg"}
```

Modes `blocked` and `probe-block` announce their PID after receiving a real input
byte or entering the probe, respectively. They sleep and must be terminated by
the recorder. `slow` forwards whole RGBA frames to the real encoder with an
80 ms delay per frame; let it finalize normally, then decode every frame and
check duration, PTS and duplicate counters. `error`, `empty`, `wrong-banner` and
`flood` exercise recoverable failures. The blocking modes have no descendants.
For every killed fixture verify the announced PID no longer exists.

A hostile executable can create arbitrary descendants; these fixtures do not
claim process-tree supervision. The real runtime requires a trusted FFmpeg.
Keep frame timing measurements separate from correctness assertions, record
build/hardware/environment and preserve raw samples. A cross-link check is not
native execution on that target.

## Device audio and live mux

`Tests/Consumer/Smokes/LiveAudio.sx` owns its source and records three short tones
with matching flashes. Startup uses the canonical `Fixture.configure` system
method reference; injected resource arguments remain borrows. Run `normal` and
`variable` on a real device. The program produces quiet application tones; it
captures no microphone or system audio. Decode all video/audio frames, compare
marker onsets, PCM tone durations and equal track duration, and inspect packet PTS.
The mono/stereo sample counter remains separate from video slots.

Modes `cancel`, `cancel-prepare`, `shutdown`, `early-stop`, `conflict` and
`conflict-late` cover lifecycle and exclusive outputs. `clock-error` expects an
incoherent device clock (the observed dummy driver provides that test condition).
Every frame checks a public input snapshot. `blocked`, `mux-cancel` and
`mux-shutdown` take an additional marker path; their proxy announces its PID,
then the consumer continues at least 30 input frames before cancelling/quitting.
Check process reaping and absence of output/private directories. Proxy modes
`mux-block` and `no-aac` affect only the final mux, forwarding live video encoding
to the qualified FFmpeg. `slow` delays live video frames but forwards the mux;
brief visual markers may be missed at this capture cadence. Audio must retain
three 100 ms tones at the application’s actual marker times, without duplication.

`Tests/RecordingAudio.sx` additionally exercises queue overflow, a closed PCM
file and cancellation before the first block without requiring a GPU. Each case
checks that detachment permits another capture and that the private file closes.
