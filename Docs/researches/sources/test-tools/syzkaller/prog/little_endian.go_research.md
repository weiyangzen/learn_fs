# sources/test-tools/syzkaller/prog/little_endian.go

Purpose: provides the package-level host byte order for supported little-endian builds.

Important APIs/types/functions: under build tags `amd64 || 386 || arm64 || arm || mips64le || ppc64le || riscv64`, declares `var HostEndian = binary.LittleEndian`.

Control flow and state: no runtime control flow; architecture build tags select this file. `HostEndian` is global immutable-by-convention state.

Dependencies and integration: imports `encoding/binary`; paired with `big_endian.go`. Code needing target byte order should still rely on type `BinaryFormat`, not host endianness.

Risks: new little-endian architectures need build-tag updates. Duplicate or missing tags would cause compile failures or wrong host encoding.

Test signals: no direct tests; most CI architectures indirectly compile this file, and executor serialization tests cover explicit big-endian target formats separately.
