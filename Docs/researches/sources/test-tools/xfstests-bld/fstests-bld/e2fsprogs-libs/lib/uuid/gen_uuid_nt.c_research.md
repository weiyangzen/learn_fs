# sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/uuid/gen_uuid_nt.c

## Purpose
`gen_uuid_nt.c` provides the Windows/NT implementation of `uuid_generate()` using operating-system UUID APIs.

## Important APIs, Types, and Functions
Public function is `uuid_generate(uuid_t out)`. Internal `Nt5()` inspects the TEB/PEB OS major version to choose behavior.

## Control Flow
For NT 5 and later it calls `UuidCreate()` and copies the resulting `UUID` bytes. For older systems it calls `UuidCreateSequential()` so time/node based UUID behavior is preserved where needed.

## State, Persistence, Dependencies, Risks, and Test Signals
There is no library-managed persistent state. Dependencies are Windows RPC UUID APIs and internal TEB/PEB layout declarations. Risks include relying on undocumented `NtCurrentTeb()`/PEB offsets, Windows version detection drift, and byte layout compatibility with libuuid's `uuid_t`. Test signals are successful Windows builds and generated UUIDs with valid variant/version fields.
