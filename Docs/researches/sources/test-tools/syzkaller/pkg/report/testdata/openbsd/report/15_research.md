# sources/test-tools/syzkaller/pkg/report/testdata/openbsd/report/15

## Purpose

This short OpenBSD fixture expects the unusual title `panic: kernel diagnostic assertion "tname->un_flags serialport: VM disconnected.` It captures a truncated or interleaved console session where syzkaller program lines and a VM disconnection message interrupt an assertion panic.

## Important APIs, Types, and Functions

Reporter behavior under test includes partial panic extraction, title preservation from `TITLE:`, and tolerance of serial transport artifacts. The only source-level operations visible are syzkaller `mknod` calls and the panic prefix `kernel diagnostic assertion "tname->un_flags`; no complete stack is present.

## Control Flow

The file shows syzkaller program fragments creating `./bus`, then a panic line that is cut by `serialport: VM disconnected.` There is no DDB trace, register block, or reboot trailer. The parser must still recognize the panic start and preserve the truncated evidence as the report body.

## State and Persistence Behavior

The fixture persists test-program calls, a partial assertion expression, and a transport-disconnect suffix. Parser state should classify the crash based on the available panic line but treat the report as low-context evidence.

## Dependencies and Integration Points

This integrates OpenBSD panic parsing with syzkaller's VM/serial output collection. It protects the path that ingests crashes even when the VM dies before full DDB output is available.

## Risks and Edge Cases

The greatest risk is discarding the crash because the assertion line is incomplete. Another risk is treating `serialport: VM disconnected` as part of a stable kernel assertion; here it is intentionally present in the expected title, so the fixture documents current parser behavior around truncated console text.

## Test Signals

A passing test returns the exact expected truncated title and produces a non-empty report containing the `mknod` repro lines plus the partial panic line.
