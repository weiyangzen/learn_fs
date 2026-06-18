## sources/test-tools/syzkaller/syz-manager/hub_test.go

`TestMatchDomains` exercises syz-manager hub domain matching. It covers empty domains, OS-only domains, malformed/trailing slash domains, same/different first-level domains, and differing second-level fuzzing dimensions. Expected booleans control whether received programs are treated as minimized and/or smashed.

The test guards an important heuristic for cross-manager corpus handling. It does not cover RPC connection, auth, program parsing, repro queueing, or stats.
