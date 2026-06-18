# sources/test-tools/syzkaller/pkg/subsystem/raw_extractor_test.go

## Purpose

This test file validates the raw subsystem extractor with a small synthetic subsystem list before higher-level voting or parent filtering is involved.

## Important APIs, Types, And Functions

`TestSubsystemExtractor` defines `ioUring`, `security`, and `net` subsystems. It checks `makeRawExtractor`, `FromPath`, and `FromProg`, including a subsystem mapped by `Syscalls` (`syz_io_uring_setup`) and paths that match multiple subsystems.

## Control Flow, State, Dependencies, And Integration

The test first verifies direct path matching, then feeds syzkaller program text into `FromProg`. It depends on `prog.CallSet` parsing syscall names from repro snippets. Assertions use `ElementsMatch` because result order comes from maps.

## Risks And Test Signals

The file catches regressions in exclude handling (`security/selinux`), overlapping paths (`net/ipv6/calipso.c`), and syscall evidence extraction. It also confirms unrelated syz calls do not spuriously map to subsystems. It does not cover malformed program parsing beyond relying on production tolerance.
