## sources/storage-engines/rocksdb/table/block_based/block_test.cc

Purpose: comprehensive unit tests for block encoding/decoding, data/index/meta block iteration, read-amplification accounting, index search, user-defined timestamps, separated KV storage, value-delta encoding, block footer feature flags, per-KV checksums, and corruption handling.

Important APIs/types/functions: helpers `GenerateInternalKey()`, `GenerateRandomKVs()`, `GetBlockContents()`, `CheckBlockContents()`, `AddIndexBlockEntry()`, and `GenerateRandomIndexEntries()` build synthetic block contents. Fixtures include `BlockTest`, `IndexBlockTest`, `BlockPerKVChecksumTest`, `DataBlockKVChecksumTest`, `IndexBlockKVChecksumTest`, `MetaIndexBlockKVChecksumTest`, corruption-test subclasses, and `MetaBlockEntryCorruptionTest`.

Control flow: tests construct `BlockBuilder` instances with parameterized encoding options, finish raw blocks, create `Block`/typed cache wrappers, and use data/index/meta iterators to scan and seek. Index tests validate key/value decoding, optional first internal key, value-delta handles, binary/interpolation/auto search, and uniformity detection. Checksum tests generate protection info, inspect checksum bytes, use sync points to count verification, and corrupt decoded values to require corruption statuses.

State and persistence behavior: no files are required except DB fixture setup for option validation. Serialized state under test is raw block bytes: entry varints, key deltas, values or separated value section, restart arrays, data block footer, optional hash index, and per-KV checksum side metadata initialized in `Block`. Read amplification tests maintain statistics counters for total and useful bytes.

Dependencies/integration points: depends on `Block`, `BlockBuilder`, `BlockCreateContext`, `DataBlockFooter`, `BlockBasedTable` constants, DB test utilities, internal-key formatting, comparators, slice transforms, protection checksums, sync points, and table format `IndexValue`.

Risks: several tests rely on internal test-only accessors and sync-point names, making them sensitive to refactors. Corruption tests mutate byte offsets and assume compact varint sizes in small synthetic blocks. Interpolation search behavior depends on key distribution assumptions.

Test signals: broad parameter matrices cover delta/no-delta, timestamp persistence, binary/hash data index, restart intervals, separated KV, index search type, first key inclusion, user-vs-internal index keys, uniform/non-uniform distributions, checksum lengths, and corruption for data/index/meta blocks.
