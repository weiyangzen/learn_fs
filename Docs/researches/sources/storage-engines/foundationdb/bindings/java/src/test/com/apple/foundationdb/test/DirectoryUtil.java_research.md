# sources/storage-engines/foundationdb/bindings/java/src/test/com/apple/foundationdb/test/DirectoryUtil.java

Purpose: helper methods for converting stack entries into directory-layer tuples and paths, plus common directory error reporting.

Important APIs and flow: `TuplePopper` repeatedly pops a tuple length followed by that many items and builds `Tuple.fromItems`. `popTuples`, `popTuple`, `popPaths`, and `popPath` expose async helpers returning tuples or `List<String>` paths. `pushError` pushes `DIRECTORY_ERROR` and appends null to the directory list when the operation's enum says it creates a directory.

State and persistence: only transient local lists. It depends on `Instruction.popParam/popParams`, `AsyncUtil.whileTrue`, `Tuple`, and `StackUtils`. Risks include assuming path tuple elements are strings, asynchronous executor ordering, and the handle-list side effect in error paths. Signal is indirect through directory stack tests.
