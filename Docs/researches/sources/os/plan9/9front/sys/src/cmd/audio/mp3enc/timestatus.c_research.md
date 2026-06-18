# File Research: sources/os/plan9/9front/sys/src/cmd/audio/mp3enc/timestatus.c

This file implements command-line progress reporting for encoding and decoding.

Key responsibilities:
- Tracks elapsed real time and CPU time for encoding.
- Estimates total encode time and ETA from current frame progress.
- Computes encode speed relative to realtime playback.
- Prints one-line updating progress status to `stderr`.
- Optionally integrates bitrate histogram display when `BRHIST` is enabled.
- Prints decoder progress for MP3 input frames.

Important functions:
- `ts_calc_times(...)`: computes estimated total time and speed index.
- `ts_time_decompose(...)`: formats seconds as `mm:ss`, `hh:mm:ss`, or large-hour text.
- `timestatus(...)`: main encoding progress renderer.
- `timestatus_finish()`: emits final newline.
- `timestatus_klemm(...)`: throttled public progress updater controlled by `silent` and `update_interval`.
- `decoder_progress(...)`: prints decoder frame number, total frames, bitrate, and joint-stereo mode transition hints.
- `decoder_progress_finish(...)`: emits decoder final newline.

Dependencies:
- Includes `lame.h`, `main.h`, `lametime.h`, and `timestatus.h`.
- Uses `GetRealTime()` and `GetCPUTime()` from `lametime.c`.
- Uses global UI controls such as `silent`, `update_interval`, and optional `brhist`.

Notable behavior:
- `timestatus()` uses static state for start times and an initialization workaround.
- Progress output is carriage-return based and intended for interactive terminals.
- Speed display is in `x` realtime units by default.
- `decoder_progress()` keeps static previous joint-stereo mode extension state to show transitions.

Risks and edge cases:
- Uses static state, so multiple concurrent encodes in the same process would share progress timing.
- `ts_calc_times()` asserts samplerate is 8000..48000.
- ETA is computed as unsigned subtraction after casting; if estimates go backward, display can be odd.
- Output is hard-wired to `stderr`.
