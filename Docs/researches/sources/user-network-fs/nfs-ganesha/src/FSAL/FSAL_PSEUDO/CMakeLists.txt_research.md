# sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_PSEUDO/CMakeLists.txt

## Purpose
Builds the PSEUDO FSAL object library.

## Important APIs, Types, and Functions
Adds `-D__USE_GNU`, defines `fsalpseudo_LIB_SRCS`, builds OBJECT library `fsalpseudo`, applies sanitizers, and sets `-fPIC`.

## Control Flow
Compiles `handle.c`, `pseudofs_methods.h`, `main.c`, and `export.c`; adds LTTng generated-header dependencies when enabled.

## State and Persistence Behavior
No runtime state; build-only file.

## Dependencies and Integration Points
Integrates PSEUDO sources into the wider Ganesha CMake build.

## Risks
OBJECT library installation/linkage is controlled elsewhere. `LIB_PREFIX` is set but unused here.

## Test Signals
Successful compilation of `fsalpseudo` with sanitizer and optional LTTng settings.
