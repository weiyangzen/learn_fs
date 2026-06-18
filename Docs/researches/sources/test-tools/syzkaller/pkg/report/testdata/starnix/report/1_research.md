# sources/test-tools/syzkaller/pkg/report/testdata/starnix/report/1

Purpose: Starnix/Fuchsia reporter fixture for a Rust panic in vendored route-netlink parsing. Expected title is `starnix kernel panic in third_party/rust_crates/vendor/netlink-packet-route-NUM.NUM.NUM/src/rtnl/link/nlas/link_infos.rs`.

Important parser APIs and patterns: handled by `starnixOopses` in `fuchsia.go`. The title captures the panicking source path from `info=panicked at ...` and uses shared dynamic-title replacement to normalize version `0.17.0` to `NUM.NUM.NUM`. Stack frames are matched by `starnixFramePatterns`, including prefixed frames and continuation lines.

Control flow: the log begins with route netlink socket creation, emits `STARNIX KERNEL PANIC`, panics at `link_infos.rs:1636:41` with `range end index 4 out of range for slice of length 3`, then prints module BuildIDs and a Rust backtrace. The stack moves from Rust panic hooks through slice indexing, `netlink_packet_route` parsers, `socket_netlink.rs::write`, socket sendmsg handling, syscall dispatch, and restricted executor task execution. A `REPORT:` block captures the shortened expected report.

State and persistence: static fixture preserving component monikers, thread labels, BuildIDs, Rust source paths, and a malformed netlink payload failure path.

Dependencies and integration: validates Starnix title sanitization for dependency versions, backtrace parsing with inline-style `#0.3` frames, and tolerance for unrelated component warnings inside a stack.

Risks: version normalization is important for deduplication across crate upgrades. Backtrace continuation lines without Starnix prefixes can be dropped if `shortenStarnixPanicReport` thresholds are too strict.

Test signals: exact version-normalized title; key frames include `link_infos.rs:1636`, `socket_netlink.rs:904`, and `sys_sendmsg`.
