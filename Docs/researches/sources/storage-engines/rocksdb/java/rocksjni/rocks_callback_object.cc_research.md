<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/rocks_callback_object.cc -->
# sources/storage-engines/rocksdb/java/rocksjni/rocks_callback_object.cc

Purpose: Provides base disposal for Java callback objects backed by native subclasses of `JniCallback`.

Important APIs/types/functions: `Java_org_rocksdb_RocksCallbackObject_disposeInternal` deletes a native pointer as `ROCKSDB_NAMESPACE::JniCallback*`.

Control flow: Java callback wrappers eventually call the base disposer with a native callback handle. The function relies on virtual destructors so deleting through `JniCallback*` destroys the actual callback subtype.

State and persistence behavior: It frees native callback state, including global Java references owned by `JniCallback`. No persistent storage is touched.

Dependencies and integration points: Includes generated `org_rocksdb_RocksCallbackObject.h` and `jnicallback.h`. It is shared by callback families such as comparators, table filters, trace writers, and listeners.

Risks: The TODO documents the key contract: deletion through the base pointer is only safe if all callback inheritance paths have virtual destructors. Passing a non-`JniCallback` handle or double-disposing will be unsafe. Callback lifetimes must also outlive RocksDB native users.

Test signals: Tests should create and dispose concrete callback subclasses, use ASAN/leak checks, and verify callbacks are not invoked after Java disposal or after RocksDB takes ownership.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/rocksjni/rocks_callback_object.cc -->
