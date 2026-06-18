# File Research: sources/os/plan9/9front/sys/src/cmd/postscript/postio/postio.mk

`postio.mk` builds and installs the PostScript printer I/O manager.

Build behavior:
- Uses `/bin/make`, `SYSTEM=V9`, `VERSION=3.3.2`.
- Supports optional Datakit configuration through `DKLIB`, `DKHOST`, `DKSTREAMS`, `DKHOSTDIR`, and extra include/library paths.
- Objects are `postio.o`, `ifdef.o`, and `slowsend.o`.
- Headers are `postio.h`, `ifdef.h`, and common `gen.h`.
- `postio` target dynamically sets CFLAGS and DKLIB depending on `SYSTEM`, `DKHOST`, and `DKSTREAMS`, then reinvokes make on `compile`.
- On V9 it links with `-lipc`; on System V DKHOST it can link with `-ldk`.
- Installs executable and manpage, but no prologue library file.
- `changes` rewrites make variables in place.

This makefile matters because `postio`’s compiled behavior is strongly controlled by `SYSTEM` and Datakit macros.
