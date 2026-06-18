# sources/storage-engines/rocksdb/util/gflags_compat.h

Purpose: compatibility shim for differences across gflags versions.

Important definitions: includes `<gflags/gflags.h>`, defines `GFLAGS_NAMESPACE` as `google` if older gflags did not define it, and defines fallback `DEFINE_uint32`/`DECLARE_uint32` in terms of `DEFINE_int32` plus a `uint32_t&` alias.

Control flow: compile-time macro fallback only.

State and persistence: gflags globals are process state only. The fallback creates an internal int32 flag and exposes a reinterpret-cast uint32 reference.

Dependencies and integration: used by tests/benchmarks needing portable gflags APIs, including `dynamic_bloom_test.cc` and `filter_bench.cc`.

Risks: the fallback `uint32_t&` alias relies on representation-compatible reinterpretation of an int32 flag, which is pragmatic but not type-safe. Negative command-line values could map unexpectedly through unsigned access.

Test signals: indirectly exercised by gflags-dependent tests/benchmarks when built with older gflags.
