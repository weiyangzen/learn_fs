# sources/storage-engines/foundationdb/bindings/ruby/tests/tester.rb

Purpose: This is the Ruby binding tester runner. It executes tuple-encoded test instructions stored in FoundationDB and normalizes Ruby binding behavior for cross-language comparison.

Important APIs and types: `Stack` resolves futures and errors, `Instruction` wraps operation context, and `Tester` manages instruction iteration, transactions, threads, range packing, stack logging, watch/locality unit tests, and directory extension dispatch.

Control flow: Startup loads local library files, selects the requested API version, opens the database, then reads instructions under a tuple range. `Tester#run` decodes each operation, selects database/current transaction/snapshot target by suffix, executes database, transaction, tuple, directory, threading, and embedded unit-test operations, and catches `FDB::Error` as packed error tuples.

State and persistence behavior: It keeps in-memory stacks, a transaction map protected by a monitor, last read/committed version, child threads, and directory tester state. Persistent effects are whatever the instruction stream requests plus `LOG_STACK` output.

Dependencies and integration points: It depends on `fdb`, `fdbtuple`, `fdblocality`, `directory_extension`, Ruby threads/monitor, and the live FoundationDB cluster. It is the primary broad integration test for the Ruby binding.

Risks: Requires a live cluster and exact agreement with the binding tester instruction spec. Some operations rely on Ruby lazy futures converting through `to_s`/numeric methods. Embedded unit tests are timing-sensitive for watches and locality.

Test signals: It covers API-version guards, options, reads/writes/ranges/selectors, atomic ops, conflict ranges, commits/resets/cancel, approximate size, versionstamps, tuple operations, directory semantics, watches, locality, stack logging, and concurrent tester threads.
