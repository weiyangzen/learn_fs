# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/u9fs/fcall.h

- Role: Defines the 9P2000 `Fcall` structure, message type constants, wire-size constants, and little-endian packing macros.
- Key declarations: `convM2S`, `convS2M`, `convM2D`, `convD2M`, `sizeD2M`, `fcallconv`, `dirconv`, `dirmodeconv`, and `read9pmsg`.
- Protocol model: Covers version/auth/attach/walk/open/create/read/write/clunk/remove/stat/wstat fields in one union-like struct.
- Integration: Central protocol header for u9fs server and old/new protocol conversion code.
- Risks/notes: Macros like `PBIT32` expand to multiple statements without `do { } while(0)`, so callers must use them carefully.
