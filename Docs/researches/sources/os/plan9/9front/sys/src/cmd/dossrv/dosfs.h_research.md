# File Research: sources/os/plan9/9front/sys/src/cmd/dossrv/dosfs.h

## Purpose
Defines 9P message size limits and shared request/reply buffers for `dossrv`.

## Key Contents
- `Maxfdata = IOUNIT`
- `Maxiosize = IOHDRSZ + Maxfdata`
- Declares global `Fcall *req`, `Fcall *rep`, reply data buffer, and stat buffer.

## Notes
This header centralizes the server’s maximum 9P payload sizing for both the main loop and request handlers.
