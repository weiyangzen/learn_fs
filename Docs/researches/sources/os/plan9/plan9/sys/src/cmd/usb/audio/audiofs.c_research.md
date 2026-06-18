# File Research: sources/os/plan9/plan9/sys/src/cmd/usb/audio/audiofs.c

Read fully: 939 lines, 17739 bytes. SHA-256 prefix: `9293e810abca627c`.

This file implements the small 9P file server exported by `usbaudio`. It serves a directory with `volume`, `audioctl`, and `audiostat`, mounts it under `/dev` by default, optionally posts `/srv`, and names USB endpoint data files as `audio` and `audioin`.

The server implements 9P handlers for version, attach, walk, open, read, write, clunk, stat, and rejects create/remove/wstat/auth. `volume` provides legacy percentage-style controls; `audioctl` reports changed controls and accepts textual control writes; `audiostat` is present in the directory but has no special read content in this file.

`Audioctldata` stores per-fid last-sent control values and buffered text. Reads from `audioctl` block off-line via `Worker` threads until a control change arrives; `ctlevent()` wakes workers after control updates. `rwrite()` parses control lines and sends serialized requests over `controlchan`, waiting on `replchan` for success/errors.

Integration: `serve()` is started by `audio.c`; it uses `setcontrol()` through `controlproc`, Plan 9 `Fcall` marshalling, and endpoint `devctl("name audio")` binding.

Risk notes: comments note a namespace bug: `/dev/audio` and `/dev/audioin` are created via endpoint name binding rather than being real served files, so mounting from another namespace may not expose them as expected. Blocking reads rely on careful worker/fid locking and flush handling.
