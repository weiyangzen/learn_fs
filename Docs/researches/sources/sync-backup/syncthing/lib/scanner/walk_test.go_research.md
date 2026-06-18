# sources/sync-backup/syncthing/lib/scanner/walk_test.go

Purpose: exercises scanner walking, hashing, ignore handling, Unicode normalization, ownership capture, cancellation, and block verification. It builds fake and basic filesystems, drives `Walk`, `Blocks`, `HashFile`, and helpers such as `walkDir`, and compares returned `protocol.FileInfo` values against expected file lists.

Important APIs and control flow: `newTestFs` constructs a representative tree with `.stignore` includes. `TestWalk` and `TestWalkSub` validate full and subdirectory scans with inherited ignore rules. `TestVerify` checks block hash verification against exact, extended, truncated, and mutated readers. Normalization tests run twice to model rename-on-scan behavior and Darwin CaseFS behavior. Cancellation is stressed with `infiniteFS` and multiple hashers. Other tests cover symlinks, block-size hysteresis from `CurrentFiler`, receive-only local flags, POSIX/Windows ownership metadata, non-existing sub paths, ignored-directory skipping, and include patterns requiring recursion into otherwise ignored trees.

State and persistence: all state is test-local fake/basic filesystem content, fake current-file maps, and event logger lifetimes. No durable persistence is created beyond temp directories.

Dependencies and integration: depends on `lib/fs`, `lib/ignore`, `lib/protocol`, `lib/events`, `lib/rand`, Unicode normalization, and scanner package internals. It is a high-signal integration test for scanner behavior as consumed by model indexing.

Risks: timing-sensitive cancellation and platform-specific normalization/ownership tests can be flaky if filesystem abstractions change. Some helper assumptions support only simple one-block expected data. Test signals are broad and target historical issues 1507, 4799, 4841, 5385, and 6487.
