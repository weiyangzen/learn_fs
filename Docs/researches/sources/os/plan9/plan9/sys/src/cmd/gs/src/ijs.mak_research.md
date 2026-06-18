# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/ijs.mak

Partial makefile for building the IJS client library within Ghostscript.

Key points:
- Requires callers to define `IJSSRCDIR`, `IJSEXECTYPE`, and `BINDIR`.
- Defines IJS source, generated, object, include, and compiler variables.
- Builds `ijslib.dev` from `ijs.o`, `ijs_server.o`, `ijs_client.o`, and `ijs_exec_$(IJSEXECTYPE).o`.
- Provides Unix and Windows exec rules for `ijs_exec_unix.c` and `ijs_exec_win.c`.
- Provides clean targets and example client/server targets.
- Comments flag known issues: clean target deletes too broadly, example linking is not portable/policy clean, and Windows exec cannot compile with `/Za` because it needs `windows.h`.

Research relevance:
- Build-system glue for Ghostscript’s IJS inkjet-server client support.
