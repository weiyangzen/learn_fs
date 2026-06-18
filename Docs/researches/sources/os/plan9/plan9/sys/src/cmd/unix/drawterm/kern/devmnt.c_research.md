# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/kern/devmnt.c

Implements Plan 9 mount device `#M`, the 9P client and RPC multiplexer for mounted remote file servers.

Key behavior:
- Negotiates `Tversion/Rversion` once per server channel and creates an `Mnt` mux object.
- Implements attach/auth, walk, stat, open, create, clunk, remove, wstat, read, and write by building 9P `Fcall` requests.
- Allocates RPC tags from a bitmap and reuses `Mntrpc` objects.
- Queues outstanding RPCs on a mount connection and matches replies by tag.
- Gates transport reads so only one process reads from the shared server channel at a time.
- Supports flush allocation and cleanup for interrupted RPCs.
- Fixes returned directory entries to use local device type/dev numbers.
- Supports optional cache integration through `CCACHE`, `cread`, `cwrite`, and `cupdate`.

Important interfaces:
- `mntversion`, `mntauth`, and `mntchan` are callable outside the devtab methods.
- `mountrpc`, `mountio`, `mntrpcread`, and `mountmux` are the core RPC path.
- `mntdevtab` registers device character `M`.

Notable risks:
- Correctness depends on tag lifecycle and serialized shared-channel reads.
- `mntchk` panics on inconsistent channel/mount state.
- Reply message sizes greater than negotiated `msize` cause queue discard and mount RPC failure.
