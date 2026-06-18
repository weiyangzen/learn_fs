# sources/test-tools/syzkaller/sys/syz-extract/openbsd.go

Purpose: OpenBSD backend for constant extraction.

Important APIs/types/functions: `openbsd.prepare`, `openbsd.prepareArch`, and `openbsd.processFile`.

Control flow: requires `-build`; symlinks amd64 include directories into the build dir as `amd64` and `machine`; composes kernel include flags; adds alternate `SYS___*` names for known syscall naming quirks; extracts with `cc`; and maps alternate values back to original constants.

State and persistence: creates build-dir symlinks and appends compatibility const probes.

Dependencies and integration points: depends on OpenBSD source layout, system C compiler, and shared `fetch.go`.

Risks: only amd64 is represented, and syscall quirk list must be maintained as OpenBSD changes names. Existing symlink paths in build dir cause preparation failure.

Test signals: downstream OpenBSD neutralizer tests depend on correct constants but no direct extraction unit test exists.
