# sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/uuid/uuid.pc.in

Purpose: `uuid.pc.in` is the pkg-config metadata template for libuuid.

Important APIs, types, and functions: it defines pkg-config fields `prefix`, `exec_prefix`, `libdir`, `includedir`, `Name`, `Description`, `Version`, `Libs`, and `Cflags`. The key consumer outputs are `-L${libdir} -luuid` and `-I${includedir}`.

Control flow: no runtime control flow. Build-time substitution replaces `@prefix@`, `@exec_prefix@`, `@libdir@`, `@includedir@`, and `@E2FSPROGS_VERSION@`.

State and persistence: installed metadata persists for downstream build systems using `pkg-config --libs uuid` or `pkg-config --cflags uuid`.

Dependencies and integration points: depends on the e2fsprogs substitution pipeline. It must align with the actual installation directories used by the library and public headers.

Risks: incorrect substitution or install paths cause downstream compile/link failures. Version mismatches can confuse dependency resolution.

Test signals: run `pkg-config --cflags --libs` against an installed build and compile a small program including `<uuid/uuid.h>` and linking with `-luuid`.
