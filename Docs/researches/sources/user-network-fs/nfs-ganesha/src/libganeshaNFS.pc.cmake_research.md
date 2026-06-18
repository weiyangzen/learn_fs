# sources/user-network-fs/nfs-ganesha/src/libganeshaNFS.pc.cmake

## Purpose
This CMake template generates the `pkg-config` metadata for the `libganeshaNFS` fuselike library.

## Important APIs, Types, And Control Flow
The template sets `prefix`, `exec_prefix`, `libdir`, and `includedir`, then emits package fields `Name`, `Description`, empty `Requires`, version from `@GANESHA_MAJOR_VERSION@@GANESHA_MINOR_VERSION@`, linker flags `-L... -lganeshaNFS`, and include flags from `@INCLUDE_INSTALL_DIR@`.

## State And Persistence
The generated `.pc` file is an installed build artifact. It persists install-time paths and version substitutions.

## Dependencies And Integration Points
It is processed by CMake configure/install logic and consumed by external builds using `pkg-config` to find Ganesha's library and headers.

## Risks And Test Signals
Version concatenation without a separator may be intentional but should be verified. Risks include wrong `LIB_SUFFIX`, wrong include install directory, and missing dependency libraries in `Requires`/`Libs`. Tests should run `pkg-config --cflags --libs libganeshaNFS` from an install tree and compile a small external consumer.
