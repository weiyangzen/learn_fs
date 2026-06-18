<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/libcap/contrib/capso/Makefile -->
# sources/security-integrity/libcap/contrib/capso/Makefile

## Purpose
Build recipe for `capso`, a shared-object file-capability demonstration that can bind to TCP port 80.

## Important APIs, Types, And Functions
Targets `bind`, `capso.o`, `capso.so`, `../../libcap/loader.txt`, and `clean`. Adds `-fPIC`, embeds `LIBCAP_VERSION` and `SHARED_LOADER`, links with libcap and libdl, and runs `sudo setcap cap_net_bind_service=p capso.so`.

## Control Flow
Builds the shared object with custom entry point `__so_start`, sets file capability on it, then builds the unprivileged `bind` program against `capso.so`.

## State And Persistence Behavior
Creates `capso.o`, `capso.so`, `bind`, and persists a file capability xattr on `capso.so`.

## Dependencies And Integration Points
Depends on in-tree libcap, loader metadata, sudo/setcap, C compiler/linker, and `execable.h` support.

## Risks And Edge Cases
The makefile invokes sudo during build. File capability setting depends on filesystem xattr support and privileges.

## Test Signals
Signals are successful build, setcap, and a `bind` binary that can obtain a port-80 socket through the shared object.
<!-- END_FILE_RESEARCH: sources/security-integrity/libcap/contrib/capso/Makefile -->
