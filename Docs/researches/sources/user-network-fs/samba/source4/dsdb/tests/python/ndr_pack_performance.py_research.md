# sources/user-network-fs/samba/source4/dsdb/tests/python/ndr_pack_performance.py

## Purpose

`ndr_pack_performance.py` is a performance-oriented test module for Samba's Python NDR bindings. It repeatedly packs, unpacks, and round-trips representative security descriptors and a compressed DRS replication sample to catch performance regressions and basic serialization correctness failures.

## Important APIs, Types, and Functions

- `BIG_SD_SDDL`, `LITTLE_SD_SDDL`, `CONDITIONAL_ACE_SDDL`, and `NON_OBJECT_SDDL` provide security descriptor fixtures with many object ACEs, fewer object ACEs, a conditional ACE, and ordinary non-object ACEs.
- `SCALE` multiplies loop counts; the source notes `100` for normal performance runs and `1` for testing the test.
- `UserTests.get_desc()` converts SDDL to `security.descriptor`; `get_blob()` packs a descriptor; `get_file_blob()` reads plain or gzipped binary fixtures.
- `_test_pack()`, `_test_unpack()`, and `_test_pack_unpack()` run tight loops against `__ndr_pack__`, `__ndr_unpack__`, `ndr_pack()`, and `ndr_unpack()`.
- Replication tests use `drsuapi.DsGetNCChangesCtr6` and `testdata/replication-ndrpack-example.gz`.

## Control Flow

The test class first exposes `test_00_00_do_nothing()` as a loop-overhead baseline. For each security descriptor fixture it constructs either an unpacked descriptor or a packed blob, then runs pack-only, unpack-only, and pack-unpack loops. The pack-unpack helper records the initial packed blob and asserts the final loop output still matches, giving a minimal correctness check while measuring repeated conversion cost.

The replication sample tests read a gzipped `DsGetNCChangesCtr6` blob. One test repeatedly unpacks the sample with a lower cycle count, and the other unpacks once then repeatedly packs the generated object. These cases exercise deeper generated NDR structures than the security descriptor tests.

## State and Persistence Behavior

The module is read-only. It reads a fixture under `testdata`, creates transient Python NDR objects and byte strings, and writes no directory or filesystem state. The only durable behavior is test runtime cost, controlled by `SCALE` and per-test cycle counts.

## Dependencies and Integration Points

It depends on `samba.ndr.ndr_pack`, `samba.ndr.ndr_unpack`, `samba.dcerpc.security`, `samba.dcerpc.drsuapi`, `gzip`, and the Samba test runner. It is an integration point for Python bindings generated from IDL, security descriptor SDDL conversion, conditional ACE support, and DRS replication NDR structures.

## Risks and Edge Cases

- The suite is runtime-sensitive; `SCALE=100` can be expensive on slow or instrumented hosts.
- It has limited assertions and is mainly a performance signal, so many semantic NDR bugs would need separate tests.
- Fixture path resolution assumes the test is run from a directory where `testdata/replication-ndrpack-example.gz` is reachable.
- Conditional ACE parsing and object ACE packing are important compatibility edges for security descriptor changes.

## Test Signals

Useful signals are elapsed-time changes per pack/unpack case, successful security descriptor round-trip blob equality, ability to parse conditional ACE SDDL, and successful unpack/pack of `DsGetNCChangesCtr6` replication data without exceptions.
