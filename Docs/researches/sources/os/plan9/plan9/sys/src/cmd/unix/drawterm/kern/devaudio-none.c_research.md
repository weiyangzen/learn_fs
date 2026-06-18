# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/kern/devaudio-none.c

No-audio backend for drawterm.

Key responsibilities:
- Implements all audio device hooks by raising `"no audio support"`.
- Covers open, close, read, write, set volume, and get volume.

Role in this group:
- Selected for platforms/builds without an audio implementation.

Notable risks:
- `audiodevclose()` also errors, which can make cleanup paths observe an error even when audio was never opened.
