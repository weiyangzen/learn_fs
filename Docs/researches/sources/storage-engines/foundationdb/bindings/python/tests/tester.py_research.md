# sources/storage-engines/foundationdb/bindings/python/tests/tester.py

Purpose: This is the Python binding tester runner. It reads tuple-encoded instructions from FoundationDB, executes them against the Python binding, and writes or stacks normalized results for cross-language conformance.

Important APIs and types: `Stack` resolves futures and normalizes missing results/errors. `Instruction` wraps the current target object and stack. `Tester` manages transactions, instruction iteration, thread spawning, range result packing, stack logging, directory extension dispatch, and embedded unit tests.

Control flow: At startup it selects the requested API version, opens a database, and loads instructions under a tuple range prefix. `Tester.run` decodes each op, chooses database/current transaction/snapshot target based on suffixes, executes operations such as get/range/set/clear/conflict/commit/reset/cancel/tuple/locality/directory/unit-tests, catches `FDBError`, and pushes tuple-packed error markers. `START_THREAD` creates nested testers over other prefixes.

State and persistence behavior: It keeps in-memory stacks and a shared transaction map protected by `RLock`. Persistent effects are the actual database mutations requested by instruction streams plus optional `LOG_STACK` output truncated to 40,000 bytes per value.

Dependencies and integration points: It integrates `fdb.impl`, `fdb.tuple`, `DirectoryExtension`, and `run_unit_tests`. It is designed to be driven by FoundationDB's binding tester infrastructure.

Risks: Randomized choices among equivalent API forms are seeded, but failures can still depend on instruction ordering and concurrent tester threads. Stack future resolution must classify value absence consistently. Legacy APIs such as `sorted(..., cmp=compare)` in related tuple tests indicate version sensitivity.

Test signals: The tester validates broad binding behavior: futures, transactions, snapshot reads, range selectors, atomic ops, conflict ranges, versionstamps, tuple order, directory layer semantics, threading, waits, and the embedded Python unit suite.
