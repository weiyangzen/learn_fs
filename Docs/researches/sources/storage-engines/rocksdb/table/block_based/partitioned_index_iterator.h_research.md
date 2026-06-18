# sources/storage-engines/rocksdb/table/block_based/partitioned_index_iterator.h

Purpose: declares the flattened iterator over a partitioned index. It lets block-based table iteration consume partitioned index blocks through the same `InternalIteratorBase<IndexValue>` interface used by non-partitioned indexes.

Important APIs/types/functions: constructor captures the table, read options, comparator, top-level index iterator, caller identity, and optional compaction readahead size. It implements seek/next/prev, validity, key/user-key/value/status, readahead state transfer, and `ResetPartitionedIndexIter`/`SavePrevIndexValue`.

Control flow: the header shows a two-level model: `index_iter_` points at partition handles, while `block_iter_` points at entries inside the current index partition. Private helpers load a partition and skip empty or invalid partitions forward/backward.

State and persistence: persistent data are index blocks already stored in the SST. The iterator tracks only live traversal state: current partition iterator validity, previous partition offset, lookup context, user comparator, and block prefetcher. Unsupported methods assert because table iterators should not call them in this role.

Dependencies/integration: includes block-based table reader internals, block prefetcher, and reader common definitions. `GetReadaheadState`/`SetReadaheadState` integrate adaptive readahead state with higher-level table readers.

Risks and test signals: unsupported methods returning assertions indicate a narrow integration contract. Status deliberately treats `NotFound` from prefix indexes as non-fatal. Upper-bound checks return unknown, so higher layers cannot rely on index-level bound pruning. Test signals are indirect through table reader and partitioned index tests outside this file; this subset includes reader code that constructs this iterator.
