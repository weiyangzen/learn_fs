# sources/test-tools/syzkaller/prog/big_endian.go

Purpose: provides the package-level host byte order for big-endian builds.

Important APIs/types/functions: under build tag `s390x`, declares `var HostEndian = binary.BigEndian`.

Control flow and state: no runtime control flow; build constraints select this file at compile time. `HostEndian` is global immutable-by-convention state used by code that needs host-native byte order.

Dependencies and integration: imports `encoding/binary`; paired with `little_endian.go` so exactly one host-endian definition exists for supported architectures.

Risks: missing build tags for a new big-endian architecture would omit or misselect `HostEndian`. Any code assuming little-endian host behavior must use target-specific formats instead.

Test signals: no direct tests in this subset; endian behavior is indirectly exercised by executor serialization tests that inspect `FormatBigEndian` metadata.
