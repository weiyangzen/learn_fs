# sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/main/java/org/apache/hadoop/ozone/debug/CheckNative.java

Purpose: `CheckNative` implements `ozone debug checknative`, reporting whether Hadoop and Ozone native libraries are loaded.

Important APIs and types: It extends `AbstractSubcommand`, implements `Callable<Void>` and `DebugSubcommand`, and is registered via `@MetaInfServices`. It uses `NativeCodeLoader`, `ErasureCodeNative`, `OpensslCipher`, `ManagedRocksObjectUtils`, and `NativeLibraryLoader`.

Control flow: `call()` builds an ordered map of library names to formatted load results, loads RocksDB and rocks-tools libraries where possible, computes the widest label, and prints a compact table.

State and persistence behavior: It does not persist data. It may load native libraries into the JVM process, which is process-global state.

Dependencies and integration points: The command integrates with the extensible debug CLI and native library discovery for Hadoop, ISA-L, OpenSSL, RocksDB, and rocks-tools JNI.

Risks: Loading native libraries has side effects and can fail based on host packaging. OpenSSL reporting intentionally suppresses a cryptic failure reason when Hadoop native itself is not loaded.

Test signals: Useful signals are printed true/false statuses and library names or failure reasons; no dedicated test is in this subset.
