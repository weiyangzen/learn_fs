<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/java/jdb_bench.sh -->
# Research: sources/storage-engines/rocksdb/java/jdb_bench.sh

Purpose: Launches the Java `DbBenchmark` class with the built RocksDB JNI jar and benchmark classes on the classpath.

Important APIs/types/functions: Determines bitness using `getconf LONG_BIT`, discovers `ROCKS_JAR` with `find target -name rocksdbjni*.jar`, and runs `java -server -d$PLATFORM -XX:NewSize=4m -XX:+AggressiveOpts -Djava.library.path=target -cp ... org.rocksdb.benchmark.DbBenchmark "$@"`.

Control flow: Choose 64-bit or 32-bit mode, locate the jar in `target`, print the bitness, then forward all command-line arguments to `DbBenchmark`.

State and persistence behavior: The script does not persist state directly. The benchmark it launches may create/write a RocksDB database and benchmark output according to its flags.

Dependencies and integration points: Depends on a prior Java/native build that populated `target` and `benchmark/target/classes`, a JVM accepting the supplied flags, and `DbBenchmark.java`.

Risks and edge cases: `-d32/-d64` and `-XX:+AggressiveOpts` are obsolete/unsupported on many modern JVMs. `find` can return multiple jars, yielding an invalid classpath. The shellcheck-disabled `$@` expansion intentionally forwards arguments but may preserve legacy behavior.

Test signals: A successful run prints "Running benchmark" and `DbBenchmark` workload summaries. JVM option errors or class-not-found errors indicate target/JDK drift.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/java/jdb_bench.sh -->
