# sources/storage-engines/foundationdb/bindings/java/src/test/com/apple/foundationdb/test/Instruction.java

Purpose: per-operation facade for stack-machine execution. It parses operation suffixes, binds the proper transaction/read context, and forwards stack operations to the owning `Context`.

Important APIs and flow: constructor interprets `_DATABASE` to use `Database` contexts and no transaction, `_SNAPSHOT` to use `tr.snapshot()` for reads, or normal operations to use the current transaction. It exposes `tcx` and `readTcx` for mutation/read wrappers, `replaceTransaction` overloads for `ON_ERROR`, `releaseTransaction`, and stack push/pop/swap/clear helpers. When pushing a `CompletableFuture` tied to a transaction, it increments the transaction reference count until completion.

State and persistence: holds immutable references for one tuple instruction and mutates the shared `Context.stack`. Risks include suffix parsing contract drift, future reference leaks, use of database-level operations where transaction replacement is impossible, and preserving snapshot/non-snapshot conflict semantics. Integration is central to stack testers and directory extensions.
