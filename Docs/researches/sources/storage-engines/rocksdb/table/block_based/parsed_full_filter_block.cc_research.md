# sources/storage-engines/rocksdb/table/block_based/parsed_full_filter_block.cc

Purpose: implements the small owning wrapper for a parsed full filter block. The file turns `BlockContents` loaded from an SST filter block into an object carrying both the raw contents and a `FilterBitsReader` produced by the configured filter policy.

Important APIs/types/functions: `ParsedFullFilterBlock::ParsedFullFilterBlock(const FilterPolicy*, BlockContents&&)` moves the contents into `block_contents_` and initializes `filter_bits_reader_` with `filter_policy->GetFilterBitsReader(block_contents_.data)` when the data slice is non-empty. The destructor is defaulted out-of-line.

Control flow: construction is a single parse step: accept contents, test empty data, call the filter policy factory for a bits reader, or leave the reader null for an empty block. There is no later mutation in this implementation file.

State and persistence: the object owns or references bytes according to the moved `BlockContents` ownership mode. It does not persist anything itself; it is the cacheable in-memory representation of persisted filter block bytes.

Dependencies/integration: it includes `filter_policy_internal.h` for `FilterBitsReader` construction and is used by full and partitioned filter readers. Partitioned filter readers cache `ParsedFullFilterBlock` entries by block offset and wrap them in `FullFilterBlockReader` for actual `KeyMayMatch`/`PrefixMayMatch` probes.

Risks and test signals: callers must pass a non-null `FilterPolicy` whenever the block is non-empty. Empty blocks produce a null reader, so downstream code must preserve the convention that empty filters are treated as may-match rather than dereferencing blindly. The partitioned filter tests in this subset exercise construction indirectly through mocked cached partition blocks.
