# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/icontext.h

Declares externally visible interpreter context-state operations.

Key points:
- Includes `icstate.h` and declares GC descriptor `st_context_state`.
- Declares `set_user_params`, supplied by user-parameter implementation variants.
- Declares context allocation, load, store, and free APIs.
- Context allocation is always in local VM and can either allocate the state object or fill an existing one.
- Context free returns a mask of VM spaces freed.

Research notes:
- This header exposes context operations used by interpreter lifecycle and Display PostScript-like context management.
