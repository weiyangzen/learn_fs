# File Research: sources/os/plan9/9front/sys/src/cmd/audio/mixfs/mixfs.c

Plan 9 user-space 9P audio mixer filesystem. It presents `audio` and `volume` files, mixes multiple client writes into a single physical audio output stream, exposes mixed playback for reads, and binds the service over `/dev/audio` and `/dev/volume`.

Important contents:
- Uses Plan 9 libraries: `<u.h>`, `<libc.h>`, `<tos.h>`, `<fcall.h>`, `<thread.h>`, `<9p.h>`, and `<pcm.h>`.
- Constants define mixer buffer sizes and output format assumptions: `NBUF`, `NDELAY`, `NQUANTA`, stereo `NCHAN`, and `ABUF`.
- `Stream` tracks per-open audio state: `used`, open `mode`, `flush`, `run`, read/write positions, `QLock`, and `Rendez`.
- Global ring buffers:
  - `mixbuf[NBUF][NCHAN]` accumulates mixed client writes.
  - `lbbuf[NBUF][NCHAN]` stores last buffered/clipped output samples for read clients.
  - `mixrp` is the shared mixer read/play cursor.
- Device state includes `devaudio`, `audiofd`, `volfd`, `devlock`, volume values, PCM format state, null-device mode, and output delay.
- `s16()` reads signed little-endian 16-bit PCM samples.
- `clip16()` clamps mixed integer samples to signed 16-bit output.
- `closeaudiodev()` closes the physical output fd under `devlock`.
- `updfmt()` reads the underlying volume control to discover `fmtout` or `speed`, updating `fmt`.
- `reopendevs()` validates and opens an audio device path, discovers `/dev/audio*` when no explicit path is usable, opens the associated volume control, handles `/dev/null`, and updates output format.
- 9P handlers:
  - `fsopen()` allocates a free `Stream` for opens of `audio`.
  - `fsflush()` marks active stream requests as flushed and wakes sleepers.
  - `fsclunk()` releases per-fid stream ownership.
  - `fsread()` serves volume status or reads mixed audio from `lbbuf`.
  - `fswrite()` handles volume/control commands or writes PCM samples into `mixbuf`.
  - `fsstat()` reports pending buffered bytes for an active audio stream.
  - `fsstart()` initializes streams and starts `audioproc`.
  - `fsend()` exits all threads.
- `audioproc()` is the mixer/output loop. It wakes waiting streams, determines available samples, opens/reopens the physical device, mixes/clips/scales samples into output buffers, advances `mixrp`, converts PCM format if needed, and writes to `audiofd`.
- `threadmain()` parses `-D`, `-s`, and `-m`, installs PCM format printing, opens/closes the target device once, builds the 9P tree, posts/mounts the service, binds it into `/dev`, and exits the thread after setup.

Control-flow summary:
- Clients open `/dev/audio`; each fid gets a `Stream`.
- Writers block when their stream gets too far ahead of `mixrp`; their signed 16-bit stereo samples are added into `mixbuf`.
- `audioproc()` periodically consumes `mixbuf` at `mixrp`, applies mixer volume, stores last output in `lbbuf`, clears consumed mix slots, advances `mixrp`, converts to hardware format if needed, and writes to the selected audio device.
- Readers follow `mixrp` through `lbbuf` to observe recent mixed output and block until new mixed samples are available.
- `/dev/volume` supports local `dev`, `mix`, and `delay` commands, passes other messages to the real volume fd when present, and synthesizes status including device, mix volume, default output format, and speed.

Integration points:
- Provides a 9P service through `Srv fs` and `threadpostmountsrv()`.
- Binds the mounted `audio` and `volume` files over `/dev/audio` and `/dev/volume`.
- Uses Plan 9 audio devices such as `/dev/audio*`, `#u/audio*`, `#A/audio*`, or `/dev/null`.
- Uses `pcm` helpers `Pcmdesc`, `mkpcmdesc`, `allocpcmconv`, `pcmratio`, `pcmconv`, `freepcmconv`, and `pcmdescfmt`.

Risk and review signals:
- Device path validation is intentionally narrow, but still allows specific kernel device namespaces and `/dev/null`.
- Audio writes assume incoming data is signed 16-bit stereo little-endian matching `pcmdescdef`.
- `fsclunk()` writes `s->used = 0` without taking the stream lock, while other paths use `qlock(s)`.
- `audioproc()` reads `audiofd` outside `devlock` in several places; `closeaudiodev()` protects close/reassignment, but concurrent visibility is simple Plan 9 style rather than fully serialized.
- `fswrite()` sets `r->ofcall.count` to the input byte count before sample alignment; partial frame bytes are effectively ignored by the mixer loop.
- Null-device timing uses cycle counter/nanosecond fallback to simulate playback progress.
- Volume scaling uses exponential mapping from 0..100 to 0..65536 for about 60 dB range.

Filesystem relevance:
- This is directly filesystem-relevant. It is a user-space synthetic 9P filesystem that virtualizes `/dev/audio` and `/dev/volume`, multiplexing multiple clients onto one audio output device.
