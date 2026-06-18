# sources/test-tools/syzkaller/pkg/report/testdata/starnix/report/2

## Purpose

This fixture is a captured Starnix crash report used by the report parser tests. It models a Rust panic in `netlink_packet_route::route::next_hops::RouteNextHopBuffer::attributes` from `third_party/rust_crates/forks/netlink-packet-route-0.20.0/src/route/next_hops.rs:78:31`, with the title normalized as a Starnix kernel panic and an overflow message.

## Important Content And Control Flow

The file begins with a `TITLE:` line, then raw console output with `STARNIX KERNEL PANIC`, panic text, `SYZFATAL` EOF from the executor RPC path, Rust backtrace frames, crashsvc/klog process exception details, module BuildID listings, register dumps, memory near PC, and a final `REPORT:` block. Parser control flow exercises title extraction, report body boundaries, Rust frame recognition, and the ability to ignore surrounding Fuchsia component-manager noise.

## State, Dependencies, Integration, Risks, And Test Signals

The fixture has no executable state, but it persists a real-world log shape that report matching must continue to support. It integrates with `pkg/report` Starnix testdata and indirectly with crash deduplication and dashboard titles. Main risks are brittle parsing around interleaved WARN/INFO prefixes, path/version changes, Unicode-ish symbol formatting, and EOF lines that should not replace the kernel panic. The test signal is that Starnix reporter tests can recover the intended title and stack from this noisy multi-section log.
