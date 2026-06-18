# sources/test-tools/syzkaller/tools/syz-db/syz-db.go

Purpose: `syz-db` manipulates syzkaller corpus database files. Commands include `pack`, `unpack`, `merge`, `bench`, `print`, and `rm`, with optional target OS/arch and database version handling.

Important APIs and flow: `main` parses flags, obtains a `prog.Target` when needed, and dispatches subcommands. `pack` reads every file in a directory, preserves optional sequence suffixes in names of the form `<hash>-<seq>`, normalizes program serialization when a target is available, fixes mismatched hash keys, and writes `db.Create`. `unpack` opens the DB and writes each record to a file named by key plus optional sequence. `merge` delegates to `db.Merge` and reports deserialization failures. `bench` deserializes records, forces a GC, prints memory stats, corpus count, and call-count percentiles. `print` sorts keys and emits key plus serialized program. `rm` deserializes each program, removes calls whose metadata name contains the requested syscall string using backward iteration, saves modified programs, deletes empty records, and flushes.

State and persistence: `pack`, `merge`, and `rm` modify or create corpus DB files; `unpack` creates files under the destination directory. In-memory state is a map of DB records and temporary `prog.Prog` values. `rm` mutates the opened DB in place and requires `Flush`.

Dependencies and integration: imports syzkaller `pkg/db`, `pkg/hash`, `prog`, all `sys` descriptions for target lookup, `tool.Fail*`, and `maps/slices` helpers. It is a developer/CI utility around manager corpus files.

Risks: `pack` reads all directory entries without skipping subdirectories; target-less packing cannot validate program syntax. `rm` uses substring matching against syscall names, so broad strings can remove more calls than intended. `bench` indexes `lens[n*9/10]`, which is safe for nonzero `n` but coarse for small corpora. `print` may emit large outputs.

Test signals: `syz-db_test.go` specifically covers `rm` removing a producer call and leaving dependent uses rewritten to invalid resources rather than crashing or leaving stale references.
