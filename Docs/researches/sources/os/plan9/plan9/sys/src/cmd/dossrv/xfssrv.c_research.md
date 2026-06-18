# File Research: sources/os/plan9/plan9/sys/src/cmd/dossrv/xfssrv.c

Main program and 9P dispatch loop for `dossrv`.

Key behavior:
- Parses options for read-only mode, verbosity, default device file, stdio serving, abort-on-panic, and space/colon translation.
- Posts a service file under `#s/<name>` unless serving over stdio.
- Forks into a service process, initializes the sector cache, and dispatches 9P requests with `read9pmsg()`, `convM2S()`, handler table lookup, and `convS2M()`.
- Uses `Rerror` replies with `xerrstr()` when handlers set internal `errno`.
- Removes the posted service file at exit.
- Provides qid equality helper.

Filesystem relevance:
- This is the server shell that exposes the FAT implementation as a Plan 9 9P service.
