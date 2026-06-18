# sources/test-tools/liburing/src/ffi.c

## sources/test-tools/liburing/src/ffi.c

Purpose: Translation unit for producing an FFI-friendly liburing library variant by forcing non-inline definitions from liburing headers.

Important APIs/macros: defines `IOURINGINLINE` before including `liburing.h`; wraps Clang diagnostic suppression for `-Wmissing-prototypes`.

Control flow: compile-time only. Including `liburing.h` with `IOURINGINLINE` altered causes header functions intended for inline use to be emitted into the FFI object/library.

State and persistence: no runtime state. Produces `ffi.ol`/`ffi.os` objects and `liburing-ffi` archives/shared libraries via `src/Makefile`.

Dependencies/integration: depends on header implementation patterns in `liburing.h`, Clang/GCC warning behavior, and version map `liburing-ffi.map`.

Risks: tightly coupled to header inline semantics; changes in `liburing.h` can alter exported FFI surface. Clang warning suppression is local but masks missing prototypes in this inclusion.

Test signals: successful FFI library build/link; downstream FFI consumers linking `-luring-ffi`.
