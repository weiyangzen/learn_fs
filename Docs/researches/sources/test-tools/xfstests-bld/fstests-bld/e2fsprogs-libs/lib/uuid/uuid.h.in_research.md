# sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/uuid/uuid.h.in

Purpose: `uuid.h.in` is the public libuuid header template. It defines the ABI-facing `uuid_t` type, variant/type constants, and function prototypes.

Important APIs, types, and functions: `typedef unsigned char uuid_t[16]`; variant constants `UUID_VARIANT_NCS`, `UUID_VARIANT_DCE`, `UUID_VARIANT_MICROSOFT`, and `UUID_VARIANT_OTHER`; type constants `UUID_TYPE_DCE_TIME` and `UUID_TYPE_DCE_RANDOM`; macro `UUID_DEFINE()`; public functions for clear, compare, copy, generate, is-null, parse, unparse, time, type, and variant.

Control flow: no runtime control flow. Preprocessor flow handles `_WIN32` time includes, C++ `extern "C"`, and GCC-specific `__attribute__((unused))` for `UUID_DEFINE()`.

State and persistence: this header persists as the installed public contract. It declares functions that mutate caller-provided UUID buffers but owns no state itself.

Dependencies and integration points: included by clients as `<uuid/uuid.h>` and by private `uuidP.h`. It requires system types and time headers. Manpages in this group document the prototypes declared here. Implementations in `pack.c`, `parse.c`, `unparse.c`, `uuid_time.c`, and other libuuid files must match these prototypes.

Risks: changes are ABI/API visible. `uuid_t` as an array type has C parameter decay quirks, so documentation must be precise about output buffers. Any mismatch between this header and implementation can break builds or C++ linkage.

Test signals: compiling `tst_uuid.c` against this header validates basic declarations. ABI tests should ensure `sizeof(uuid_t) == 16` and that public prototypes remain compatible.
