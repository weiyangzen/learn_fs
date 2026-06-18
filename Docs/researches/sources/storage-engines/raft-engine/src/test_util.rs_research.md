# sources/storage-engines/raft-engine/src/test_util.rs

Purpose: this file centralizes small test helpers for constructing raft entries, constructing memtable entry indexes, and controlling panic-hook noise in tests.

Important APIs and types: `generate_entries(begin_index, end_index, data)` returns raft `Entry` values with consecutive indexes and optional data. `generate_entry_indexes` and `generate_entry_indexes_opt` build `EntryIndex` records for a half-open index range and optional `FileId`. `catch_unwind_silent` temporarily suppresses the default panic hook while catching a panic. `PanicGuard` installs a panic hook that prints a prompt before forwarding to the previous hook, then restores the previous hook on non-panicking drop.

Control flow: generators allocate vectors sized from the requested ranges and fill indexes monotonically. `catch_unwind_silent` stores the previous hook, installs a no-op hook, calls `panic::catch_unwind(AssertUnwindSafe(f))`, and restores the hook. `PanicGuard::with_prompt` stores the previous hook in an `Arc`, installs a hook that prints the prompt and invokes the previous hook, and restores on drop unless the current thread is already panicking.

State and persistence behavior: no persistent state. Panic hook manipulation is process-global and must be scoped carefully; `PanicGuard` deliberately avoids restoration during unwinding to avoid hook churn while panicking.

Dependencies and integration points: depends on raft `Entry`, memtable `EntryIndex`, and pipe-log handle types. It is used by memtable and swappy allocator tests to generate fixtures and assert panic behavior without noisy output.

Risks and invariants: range arguments are half-open and `generate_entry_indexes_opt` asserts `end_idx >= begin_idx`. Generated `EntryIndex` values use offset and length zero/one defaults and are not valid real file locations beyond tests. Panic-hook changes are global, so concurrent tests that also mutate hooks can interfere.

Test signals: this is itself support code. Its behavior is indirectly checked by tests that rely on generated indexes and silent panic catching, especially memtable panic boundary tests and allocator failure tests.
