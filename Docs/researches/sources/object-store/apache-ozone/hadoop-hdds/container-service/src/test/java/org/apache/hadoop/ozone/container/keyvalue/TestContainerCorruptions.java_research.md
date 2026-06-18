# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/keyvalue/TestContainerCorruptions.java

Purpose: enumerates reusable corruption injectors for container scanner tests, mapping each filesystem mutation to the expected `ContainerScanError.FailureType`.

Important APIs/types/functions: enum constants for missing chunks/metadata/container dirs, missing `.container` file, missing/corrupt/truncated block files, corrupt/truncated container file; `applyTo(Container<?>)`, `applyTo(Container<?>, long)`, `assertLogged(...)`, `getExpectedResult()`, `getAllParamsExcept(...)`, and `getBlock(...)`.

Control flow: each enum constant wraps a `BiConsumer<Container<?>,Long>` that deletes directories/files or mutates file content using `ContainerTestHelper.corruptFile`/`truncateFile`. `getBlock()` locates either the first `.block` file for negative IDs or a specific `<localID>.block` file under the chunks directory. Log assertions compile multiline regexes to verify scanner log output includes the expected failure type and container ID.

State and persistence behavior: mutations operate directly on the container's on-disk directory tree. Truncated block behavior intentionally maps to `MISSING_CHUNK` because a fully emptied file causes scanner chunk lookups to report all chunks missing.

Dependencies and integration points: used by `TestKeyValueContainerCheck` and reconciliation helpers. It depends on key-value file-per-block layout conventions, Apache Commons `FileUtils`, AssertJ, JUnit assertions, and `ContainerScanError`.

Risks and test signals: gives clear, reusable scan-corruption fixtures. The comment notes current support is file-per-block focused; tests using file-per-chunk or future layouts must avoid incompatible cases or extend lookup logic.
