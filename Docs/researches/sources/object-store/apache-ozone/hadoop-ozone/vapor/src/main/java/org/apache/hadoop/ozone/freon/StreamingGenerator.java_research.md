# sources/object-store/apache-ozone/hadoop-ozone/vapor/src/main/java/org/apache/hadoop/ozone/freon/StreamingGenerator.java

Purpose: Freon Vapor subcommand `strmg`/`streaming-generator` that builds a per-thread test directory and repeatedly streams a subdirectory from a local `StreamingServer` to a `StreamingClient`.

Important APIs/types/functions: `StreamingGenerator.call`, `generateBaseData`, `copyDir`, `threadRootDir`, `deleteDirRecursive`; uses `BaseFreonGenerator.runTests`, Dropwizard `Timer`, `ContentGenerator`, `DirectoryServerSource`, `DirectoryServerDestination`, `StreamingServer`, and `StreamingClient`.

Control flow: `call` initializes Freon metrics and executes `copyDir` for each generated index. On first use per thread, `copyDir` calls `generateBaseData`, which deletes the thread root, creates `streaming-0/dir1`, and writes `numberOfFiles` files of `fileSize`. Each iteration starts a server for the current source directory, streams `dir1` to the next destination directory, times the client stream, then deletes the previous source.

State/persistence: stores generated test data under `--root-dir` with child directories named after Java thread names and generation indexes. The `ThreadLocal<Integer>` counter is the per-thread state machine. Cleanup is recursive and destructive for the generated source path.

Dependencies/integration: picocli `@Command`, `@MetaInfServices(VaporSubcommand.class)`, Ozone container streaming package, Commons IO `FileUtils`, and Freon metrics.

Risks: port selection `1234 + (l % 64000)` can collide with existing processes or parallel workers. Recursive delete of `testRoot/threadName` requires safe `--root-dir` use. `ThreadLocal` state is never removed but command lifetime is short. Any stream failure leaves destination/source directories for manual inspection or cleanup.

Test signals: no direct tests in this subset. Tests should simulate one copy round with a temporary root and assert generated files move from `streaming-N` to `streaming-N+1`.
