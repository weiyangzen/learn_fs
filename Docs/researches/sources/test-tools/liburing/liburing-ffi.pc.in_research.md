# sources/test-tools/liburing/liburing-ffi.pc.in

## sources/test-tools/liburing/liburing-ffi.pc.in

Purpose: pkg-config template for the liburing FFI shared/static development package.

Important fields: `prefix`, `exec_prefix`, `libdir`, `includedir`, `Name`, `Version`, `Description`, `URL`, `Libs: -L${libdir} -luring-ffi`, and `Cflags: -I${includedir}`.

Control flow: top-level Makefile transforms placeholders `@prefix@`, `@libdir@`, `@includedir@`, `@NAME@`, and `@VERSION@` via `sed` into `liburing-ffi.pc`.

State and persistence: template is static; generated `.pc` is installed to pkgconfig dir.

Dependencies/integration: consumed by pkg-config users linking `liburing-ffi`. Version/name come from Makefile/config metadata.

Risks: does not express dependency on base `liburing` even though FFI library build includes liburing objects; this may be intentional. No `Requires` or `Libs.private`.

Test signals: generated pc file during `make install`; downstream `pkg-config --libs --cflags`.
