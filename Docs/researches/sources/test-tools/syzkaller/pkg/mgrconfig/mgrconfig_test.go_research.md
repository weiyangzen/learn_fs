# sources/test-tools/syzkaller/pkg/mgrconfig/mgrconfig_test.go

Purpose: Tests canned manager configs and syscall pattern matching from an external-package perspective.

Important tests: `TestCanned` loads every `testdata/*.cfg`, then parses the raw VM config into the correct VM-specific config type (`qemu`, `gce`, or `proxyapp`). `TestMatchSyscall` validates exact, base-name, and wildcard matching against syscall names with optional `$variant` suffixes.

Control flow and state: Canned configs are loaded through `LoadFile`, which runs full completion. VM raw JSON is loaded with `config.LoadData` into typed VM structs. Pattern tests call `MatchSyscall(call, pattern)`.

Dependencies and integration: Ensures mgrconfig stays compatible with VM package schemas and real example config files. Uses dot-import of `mgrconfig` to exercise exported API.

Risks: Canned configs rely on testdata syzkaller binaries/images existing. Pattern coverage is concise and does not include malformed or empty patterns.

Test signals: Good regression guard for config schema drift and syscall filter semantics.
