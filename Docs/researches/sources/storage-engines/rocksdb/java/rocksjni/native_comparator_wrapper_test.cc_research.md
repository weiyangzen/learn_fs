# sources/storage-engines/rocksdb/java/rocksjni/native_comparator_wrapper_test.cc

## Purpose
Provides a tiny native comparator implementation used by RocksJava's `NativeComparatorWrapperTest`. It verifies that Java can wrap a native `ROCKSDB_NAMESPACE::Comparator` in a Java comparator object, configure it on `Options`, write data, reopen the database, and observe iteration order produced by the native comparator.

## Important APIs, Types, And Functions
`NativeComparatorWrapperTestStringComparator` is a test-only `Comparator` subclass. It implements `Name`, `Compare`, `FindShortestSeparator`, and `FindShortSuccessor`. The JNI factory `Java_org_rocksdb_NativeComparatorWrapperTest_00024NativeStringComparatorWrapper_newStringComparator` creates the comparator and returns its pointer as a `jlong` with `GET_CPLUSPLUS_POINTER`.

## Control Flow
Java test class `NativeComparatorWrapperTest.NativeStringComparatorWrapper` calls `initializeNative`, which invokes the JNI `newStringComparator`. The native factory allocates `NativeComparatorWrapperTestStringComparator` and returns the handle. RocksDB later calls `Compare` during memtable/table operations and iteration; the implementation converts both `Slice` arguments to `std::string` and uses `std::string::compare` for bytewise lexicographic ordering. Separator and successor shortening are explicit no-ops, so RocksDB keeps keys unchanged during index-boundary optimization callbacks.

## State And Persistence Behavior
The comparator object has no mutable fields and persists no data itself. Its ordering affects the physical and logical ordering of keys written to the test database, so the same comparator must be supplied when reopening the DB. The JNI allocation transfers native pointer ownership into the Java `NativeComparatorWrapper` lifecycle; this file contains only the factory, while disposal is inherited from comparator-wrapper infrastructure.

## Dependencies And Integration Points
Depends on the generated nested-class JNI header `org_rocksdb_NativeComparatorWrapperTest_NativeStringComparatorWrapper.h`, `rocksdb/comparator.h`, `rocksdb/slice.h`, and pointer conversion helpers. It integrates with `NativeComparatorWrapperTest.java`, `Options.setComparator`, `RocksDB.open`, and `RocksIterator`. Because the class is inside `ROCKSDB_NAMESPACE`, it matches the comparator ABI expected by the C++ DB implementation.

## Risks And Edge Cases
`Compare` materializes both slices as `std::string`, which is acceptable for a test comparator but would be inefficient for production hot paths. No-op separator methods are legal but can reduce table-index optimization opportunities. The comparator name is fixed; changing it can make existing RocksDB data with the older comparator name fail comparator consistency checks. Since this is a native test helper, leaks or double-free behavior would surface through Java wrapper ownership rather than code in this file.

## Test Signals
The primary signal is `NativeComparatorWrapperTest.rountrip`, which writes 1,000 random string keys, sorts the expected strings with Java natural ordering, reopens the DB with the same comparator, iterates from first to last, and checks that RocksDB iteration matches the comparator's ordering. Build/link correctness is also tested by successful loading of the nested JNI symbol name containing `_00024`.
