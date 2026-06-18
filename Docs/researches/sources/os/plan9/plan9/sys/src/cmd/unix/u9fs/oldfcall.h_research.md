# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/u9fs/oldfcall.h

- Role: Declares old 9P conversion routines and old protocol opcode constants.
- Key declarations: Old message conversion, stat conversion, header sizing, and write data sizing helpers.
- Integration: Included by `u9fs.c`, `oldfcall.c`, and `fcallconv.c` for old/new protocol auto-detection and debug formatting.
- Risks/notes: Contains constants only; correctness depends on `oldfcall.c` preserving fixed legacy field layout.
