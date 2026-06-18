# File Research: sources/os/plan9/9front/sys/src/cmd/fax/receive.c

## Purpose
Command entry point for receiving a fax from stdin/stdout modem descriptors and running the post-receive hook.

## Key Elements
Parses `-v` and `-s spool`, initializes a single `Modem` on fd 0, calls `faxreceive`, logs completion, and on success executes `/sys/lib/fax/receiverc` with document id, success flag, page count, and optional FTSI.

## Dependencies
Uses `faxreceive`, `faxrlog`, Plan 9 `exec`, and the `receiverc` rc script.

## Behavior/Risks
The default control fd is `-1`, so flow-control writes are not expected during receive entry. If the receive hook `exec` fails, the program exits with `"can't exec"` after a successful fax.
