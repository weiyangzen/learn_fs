# sources/storage-engines/rocksdb/table/block_based/user_defined_index_wrapper.h

Purpose: provides wrapper classes that integrate RocksDB user-defined indexes with the existing block-based table index abstraction while still building and retaining the standard internal index.

Important APIs/types/functions: `UserDefinedIndexBuilderWrapper` derives from `IndexBuilder` and forwards `AddIndexEntry`, `OnKeyAdded`, `Finish`, size estimates, and separator behavior to an internal builder plus a `UserDefinedIndexBuilder`. `UserDefinedIndexIteratorWrapper` adapts a `UserDefinedIndexIterator` to `InternalIteratorBase<IndexValue>`. `UserDefinedIndexReaderWrapper` dispatches reads between the standard index reader and UDI reader based on primary mode or `ReadOptions::table_index_factory`.

Control flow: on writes, every index entry and key is sent to the standard builder. UDI calls parse internal keys to pass user keys plus sequence/type tags in context; parse errors are stored and returned on finish because `AddIndexEntry` cannot return status. `Finish` emits the UDI as a meta block named with `kUserDefinedIndexPrefix + name_`, then finishes the standard index. On reads, UDI iterator results are converted back into internal-key separators with seq 0/value type and cached `IndexValue` block handles.

State and persistence: persistent output includes the normal index blocks plus a UDI meta block. Runtime state includes the wrapped builders/readers, UDI name, cached status, finish flag, cached iterator result/internal key/value, and primary-mode selection.

Dependencies/integration: depends on `rocksdb/user_defined_index.h`, internal key parsing/packing, table reader index interfaces, block handles, meta block naming, and `ReadOptions` dispatch. It explicitly rejects parallel-compression split index entry APIs with assertions because that mode is validated away elsewhere.

Risks and test signals: risks include sequence/tag mishandling for duplicate user keys across snapshots, value type mapping drift when new RocksDB value types are added, unsupported `SeekForPrev`, and UDI primary mode hiding standard index read bugs. This subset has no direct UDI tests; comments reference option validation and PR discussion as integration constraints.
