# File Research: sources/os/plan9/9front/sys/src/cmd/dossrv/xfssrv.c

## Purpose
Main server loop and process setup for `dossrv`.

## Key Behavior
- Parses options: `-:` to translate colons/spaces, `-r` read-only, `-v` verbose, `-f devicefile` default filesystem, `-s` stdio mode, and `-p` abort-on-panic.
- Allocates global request/reply `Fcall` buffers and initializes the sector cache.
- In service mode, creates `/srv/dos` or `/srv/<name>`, writes a pipe fd to it, dupes the other pipe end onto stdin/stdout, and forks a detached server process.
- `io()` reads 9P messages, decodes them, dispatches through the `fcalls` table, converts internal `errno` into `Rerror`, encodes replies, and writes them back.
- Installs `fcallfmt` for verbose tracing.
- `xerrstr()` maps internal error codes to strings, using the process errstr for `Eerrstr`.
- `eqqid()` compares Plan 9 qids.

## Interfaces And Dependencies
- Includes `errstr.h` to define the error string table.
- Dispatches handlers implemented in `dosfs.c` and uses global buffers declared in `dosfs.h`.

## Notes
The process model is a classic Plan 9 service-file server: parent exits after forking, child owns the 9P loop. Stdio mode lets it be mounted or driven by another process without creating `/srv`.
