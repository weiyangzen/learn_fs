# sources/storage-engines/foundationdb/bindings/java/src/test/com/apple/foundationdb/test/Context.java

Purpose: shared execution context for the Java stack-machine testers. It owns the instruction range, shared stack, child contexts, named transaction registry, and asynchronous parameter popping semantics used by both synchronous and asynchronous runners.

Important APIs and flow: the constructor derives the instruction scan range from `Tuple.from(prefix).range()` and opens a current transaction. `run` calls subclass `executeOperations` and joins child threads. Static transaction maps implement `newTransaction`, `replaceTransaction`, `releaseTransaction`, and `getTransaction` with reference counts so pending futures can safely outlive an instruction. `popParams` recursively pops stack entries and resolves futures on `FDB.DEFAULT_EXECUTOR`, converting FDB failures to packed error bytes.

State and persistence: static maps are process-wide and keyed by printable transaction names, so thread tests share named transactions. `lastVersion` stores read/commit version data for later `SET_READ_VERSION`. Risks include global state across contexts, assert-dependent null checks, reference leaks on unexpected future paths, and process termination on runner exceptions. Integration is central to `Instruction`, `StackTester`, `AsyncStackTester`, and directory extensions.
