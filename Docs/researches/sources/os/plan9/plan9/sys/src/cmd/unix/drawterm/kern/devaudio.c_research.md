# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/kern/devaudio.c

Implements Plan 9 device `#A/audio`, exposing `audio` and `volume` files above a platform-specific backend.

Key behavior:
- Provides directory entries `.`, `audio`, and `volume`.
- Serializes `/audio` use through `audio.amode`; only one active reader or writer is allowed.
- Opens the backend on `/audio` open and closes it on final close.
- Reads from `volume` by querying every known control and formatting Plan 9-style volume lines.
- Writes to `volume` by parsing commands such as volume names, `reset`, `in`, `out`, `left`, `right`, and numeric values.
- Writes to `audio` call `audiodevwrite`; reads call `audiodevread`.
- Registers `audiodevtab` as device character `A`.

Important interfaces:
- `audiodevopen`, `audiodevclose`, `audiodevread`, `audiodevwrite`, `audiodevgetvol`, `audiodevsetvol`.
- `parsecmd` is used for textual volume commands.
- `audioswab` provides 32-bit byte swapping, though it is not used in this file.

Notable risks:
- The generic device accepts read mode for `/audio`, but the Unix backend does not support reads.
- Volume parsing has no explicit range checks before backend calls.
