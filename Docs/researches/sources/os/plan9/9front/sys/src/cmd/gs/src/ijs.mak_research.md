# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/ijs.mak

Partial makefile for building the IJS client library within Ghostscript.

Key points:
- Users must define:
  - `IJSSRCDIR`
  - `IJSEXECTYPE`
  - `BINDIR`
- Defines source/generated/object directory variables for IJS.
- Defines IJS include and compiler flags.
- Builds `ijslib.dev` from:
  - `ijs.o`
  - `ijs_server.o`
  - `ijs_client.o`
  - `ijs_exec_$(IJSEXECTYPE).o`
- Provides rules for Unix and Windows process-control implementations:
  - `ijs_exec_unix.c`
  - `ijs_exec_win.c`
- Provides clean targets:
  - `ijs.clean`
  - `ijs.config-clean`
  - `ijs.clean-not-config-clean`
- Provides example client/server build targets:
  - `ijs_client_example`
  - `ijs_server_example`
- Comments flag known issues:
  - clean target is too broad: “WRONG. MUST DELETE OBJ AND GEN FILES SELECTIVELY.”
  - example linking is not portable / policy FIXME.
  - Windows exec source cannot use `/Za` because it needs `windows.h`.

Dependencies and interactions:
- Related to `gdevijs.c` and external IJS printer/server integration.
- Consumed by the larger Ghostscript make system.

Research relevance:
- Build-system glue for Ghostscript’s IJS inkjet-server client support.
