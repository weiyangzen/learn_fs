# sources/test-tools/fio/lib/seqlock.h

Purpose: lightweight sequence lock for single-writer/multiple-reader style data snapshots.

Important APIs/types: `struct seqlock` with volatile or C++ atomic sequence, `seqlock_init`, `read_seqlock_begin`, `read_seqlock_retry`, `write_seqlock_begin`, and `write_seqlock_end`.

Control flow: readers spin until they observe an even sequence, read protected data externally, then retry if the sequence changed. Writers increment to odd at begin and store-release an even value at end.

State/persistence: one sequence counter; protected payload lives outside this struct. No writer serialization is provided by this type itself.

Dependencies/integration: depends on fio arch atomics, barriers, and `nop`. Used where fio wants low-cost lockless reads.

Risks/test signals: multiple concurrent writers require external locking. Readers can spin if a writer stalls mid-update. Tests should exercise retry behavior and memory ordering on supported architectures.
