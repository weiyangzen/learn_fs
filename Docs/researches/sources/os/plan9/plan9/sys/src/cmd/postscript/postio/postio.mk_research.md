# File Research: sources/os/plan9/plan9/sys/src/cmd/postscript/postio/postio.mk

Low-level makefile for `postio`.

Key responsibilities:
- Defines V9/default build variables, install directories, common directory, compiler/linker flags, and Datakit options.
- Builds `postio` from `postio.o`, `ifdef.o`, and `slowsend.o`.
- Installs executable and manpage.
- Provides platform-aware compile target that exports `SYSTEM`, `DKHOST`, `DKSTREAMS`, and `DKLIB` settings.
- Provides `clean`, `clobber`, and `changes`.

Important behavior:
- For V9, links with `-lipc`.
- For non-V9 with `DKHOST=TRUE`, may force `SYSTEM=SYSV`, define `DKHOST`, optionally define `DKSTREAMS`, and link `-ldk`.
- Adds `-D$SYSTEM` to `CFLAGS` before compiling.

Dependencies:
- Headers: `postio.h`, `ifdef.h`, and `../common/gen.h`.
- No shared common objects are linked, because `postio.c` provides its own logging/error path.

Risks and quirks:
- Build behavior is controlled by shell-variable mutation inside a recursive make target.
- Commented `DKHOSTDIR` guidance shows this makefile expects site-local Datakit library/header layout.
- `postio ::` target recursively invokes `compile`, so environment leakage matters.
