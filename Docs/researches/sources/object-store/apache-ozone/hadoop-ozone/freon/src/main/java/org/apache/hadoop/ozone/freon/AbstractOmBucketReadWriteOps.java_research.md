## sources/object-store/apache-ozone/hadoop-ozone/freon/src/main/java/org/apache/hadoop/ozone/freon/AbstractOmBucketReadWriteOps.java

Purpose: shared base for Freon workloads that create/list/read and write Ozone bucket paths via either Hadoop FS or Ozone bucket APIs.

Important APIs/types/functions: extends `BaseFreonGenerator` and implements `Callable<Void>`. Abstract hooks: `display`, `initialize`, `createPath`, `getReadCount`, and `create`. Concrete workflow includes `readOperations`, `writeOperations`, `create`, and `getSizeInBytes`. Picocli options configure object size, buffer size, random name length, total thread count, read-thread percentage, read operation count, and write operation count.

Control flow: `call` initializes Freon, computes read/write thread counts, prints configuration, builds `ContentGenerator` and metrics timer, then delegates to subclass `initialize`. `readOperations` precreates objects under a read path and runs concurrent list/read-count tasks. `writeOperations` creates a write path and concurrently writes batches. `create` writes random-named objects using subclass output streams.

State and persistence behavior: local state includes timers, content generator, and thread counts. Persistent effects are Ozone keys/files created in subclass storage backends.

Dependencies and integration points: used by `OmBucketReadWriteFileOps` and `OmBucketReadWriteKeyOps`; depends on Dropwizard metrics, Hadoop `StorageSize`, Ozone path constants, and `ContentGenerator`.

Risks: nested executors inside `runTests` can create high thread counts; read/write services are shutdown but not awaited after shutdown beyond completion-service takes; IOExceptions in worker tasks are logged and converted to partial counts instead of failing.

Test signals: validate subclasses with small read/write counts and assert created object counts and metrics timer increments.
