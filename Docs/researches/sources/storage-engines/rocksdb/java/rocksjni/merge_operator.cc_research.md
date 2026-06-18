# sources/storage-engines/rocksdb/java/rocksjni/merge_operator.cc

## Purpose
Implements the JNI bridge for Java `StringAppendOperator` and `UInt64AddOperator`, exposing built-in C++ `ROCKSDB_NAMESPACE::MergeOperator` factories to RocksJava. The file lets Java option objects hold a native handle to a heap-allocated `std::shared_ptr<MergeOperator>` that can be passed into DB, column-family, SST writer, and transaction configuration paths.

## Important APIs, Types, And Functions
The exported JNI entry points are `Java_org_rocksdb_StringAppendOperator_newSharedStringAppendOperator__C`, `Java_org_rocksdb_StringAppendOperator_newSharedStringAppendOperator__Ljava_lang_String_2`, `Java_org_rocksdb_StringAppendOperator_disposeInternalJni`, `Java_org_rocksdb_UInt64AddOperator_newSharedUInt64AddOperator`, and `Java_org_rocksdb_UInt64AddOperator_disposeInternalJni`. They allocate or delete `std::shared_ptr<ROCKSDB_NAMESPACE::MergeOperator>` objects, wrapping results from `MergeOperators::CreateStringAppendOperator` and `MergeOperators::CreateUInt64AddOperator`. `GET_CPLUSPLUS_POINTER` converts native pointers to `jlong` handles for Java.

## Control Flow
The char-delimiter constructor casts the Java `jchar` to `char`, constructs the C++ string append merge operator, stores the returned shared pointer in a heap-allocated shared-pointer wrapper, and returns that wrapper's address. The string-delimiter overload calls `JniUtil::copyStdString`; if copying throws or reports an exception, it returns `0` immediately, otherwise it constructs the merge operator with the copied delimiter. Disposal receives the Java handle, reinterprets it as a pointer to the heap-allocated shared pointer, and deletes only that wrapper, letting normal `shared_ptr` reference counting release the underlying merge operator when no C++ options still retain it. The UInt64 operator path follows the same allocation/disposal pattern without delimiter conversion.

## State And Persistence Behavior
This file does not persist RocksDB data directly. Its durable effect is indirect: the merge operator selected here changes how later merge operands are combined during writes, reads, flushes, and compactions. Native state consists only of heap allocations and shared ownership around `MergeOperator` instances. Java is responsible for calling the matching `disposeInternalJni` through `RocksObject` lifecycle; options or column-family options that copy the shared pointer can keep the operator alive after the Java wrapper is closed.

## Dependencies And Integration Points
The bridge depends on generated JNI headers for `StringAppendOperator` and `UInt64AddOperator`, `rocksdb/merge_operator.h`, `utilities/merge_operators.h`, `rocksjni/portal.h`, and `rocksjni/cplusplus_to_java_convert.h`. Java callers are `StringAppendOperator.java` and `UInt64AddOperator.java`, and integration usually happens through `Options.setMergeOperator`, `ColumnFamilyOptions.setMergeOperator`, `SstFileWriter`, and transaction tests that configure merge behavior for column families.

## Risks And Edge Cases
The `jchar` to `char` cast truncates non-8-bit delimiters; callers needing multi-byte or non-ASCII delimiters must use the string overload. A null or uncopyable Java string relies on `copyStdString` to signal a JNI exception and returns a null native handle. Misordered lifecycle between Java merge operators and options is mitigated by `shared_ptr`, but an invalid or double-disposed handle would still be unsafe at the JNI boundary. The file allocates with `new` and has no local RAII guard between allocation and returning the handle; current paths are simple enough that only allocation failure or JNI exceptions before allocation matter.

## Test Signals
Direct behavior is covered indirectly by Java merge tests such as `MergeTest`, `MergeVariantsTest`, `MergeCFVariantsTest`, `PutVariantsTest`, `PutCFVariantsTest`, `RocksDBTest`, and SST reader/writer tests that configure `StringAppendOperator` or `UInt64AddOperator` and assert merge results. Optimistic transaction tests also configure string append operators for default and named column families, exercising compatibility with transaction DB open paths.
