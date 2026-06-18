# sources/user-network-fs/bazil-fuse/fuse_kernel_linux.go

Purpose: This Linux-specific adapter normalizes raw open flags from FUSE kernel messages before exposing them as `OpenFlags`.

Important APIs, types, and functions: `openFlags(flags uint32) OpenFlags` clears bit `0x8000`, the 32-bit `O_LARGEFILE` bit, then converts the result to `OpenFlags`.

Control flow: The function always masks out `0x8000` and returns the remaining bits. The comments explain that this ABI bit is uninteresting for FUSE protocol consumers.

State and persistence behavior: No state or persistence.

Dependencies and integration points: Used by `fuse.go` when decoding request file flags. It makes exported open flags stable across Linux architectures and client ABI details.

Risks: If a future Linux flag meaningfully reuses this bit in FUSE context, it would be hidden. The current risk is low because the comment ties it to `O_LARGEFILE` noise.

Test signals: `serve_test.go` normalizes other Linux open flag quirks such as historical `O_CLOEXEC` leakage in some tests. `fuse_kernel_test.go` covers access mode masking after flags are converted.
