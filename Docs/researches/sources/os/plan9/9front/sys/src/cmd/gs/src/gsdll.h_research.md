# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gsdll.h

This deprecated header declares the old Ghostscript DLL API. It explicitly tells clients to use the newer API described by `API.htm` and `iapi.h`.

It defines:
- Platform calling/export conventions.
- Legacy `GSDLL_CALLBACK`.
- Global `pgsdll_callback`.
- Callback message constants for stdin, stdout, device open/close, sync, page output, resize, and polling.
- Initialization return codes `GSDLL_INIT_IN_USE` and `GSDLL_INIT_QUIT`.
- Exported legacy functions for revision, init, string execution, exit, and device locking.
- Runtime dynamic-linking function pointer typedefs.

The header has Windows, OS/2 IBM C, and Mac compatibility conditionals. It is retained for older embedding clients.
