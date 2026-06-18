# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gsexit.h

This header declares process-exit and abort hooks that clients must provide.

Functions:
- `gs_to_exit` performs client cleanup/error messaging and normally returns to the caller instead of calling `exit`.
- `gs_to_exit_with_code` is similar but also returns a PostScript error code.
- `gs_abort` handles fatal abort cleanup and may call platform-independent `gp_do_exit`.

The comments emphasize that `gs_abort` is fatal and returning from it is not a good idea.
