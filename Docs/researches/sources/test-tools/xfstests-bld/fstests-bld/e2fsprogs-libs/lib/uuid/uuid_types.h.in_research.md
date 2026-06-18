# sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/uuid/uuid_types.h.in

Purpose: `uuid_types.h.in` is a fallback integer type header for libuuid when `<inttypes.h>` is unavailable.

Important APIs, types, and functions: it defines signed and unsigned fixed-width integer typedefs (`int8_t`, `int16_t`, `int32_t`, `int64_t`, `uint8_t`, `uint16_t`, `uint32_t`, `uint64_t`) using Autoconf-substituted base C types.

Control flow: preprocessor include guard `_UUID_TYPES_H`; no runtime flow. The file depends on substitutions such as `@u_int8_t@`, `@uint16_t@`, and similar configured type names.

State and persistence: installed/generated header only. It affects compile-time type availability and ABI assumptions.

Dependencies and integration points: `uuidP.h` includes this header when `HAVE_INTTYPES_H` is not defined. Pack/unpack and time code require exact-width integer behavior.

Risks: incorrect configure substitutions break binary layout and arithmetic. Defining standard typedef names can conflict with system headers if inclusion guards or feature detection are wrong.

Test signals: configure/build on systems without `<inttypes.h>` or with simulated fallback. Compile pack/unpack/time code and assert expected type widths.
