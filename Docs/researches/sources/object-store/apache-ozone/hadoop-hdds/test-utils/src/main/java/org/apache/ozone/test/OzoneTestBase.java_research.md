# sources/object-store/apache-ozone/hadoop-hdds/test-utils/src/main/java/org/apache/ozone/test/OzoneTestBase.java

Purpose: `OzoneTestBase` is a base class for JUnit 5 tests that need the current test method name and deterministic unique lowercase object names.

Important APIs and types: It uses JUnit `TestInfo` and `@BeforeEach`, Java reflection `Method`, `Locale.ROOT`, `Objects`, and a static `AtomicInteger` counter. Public/static API includes `uniqueObjectName(String)`, while subclasses use `getTestName()` and `uniqueObjectName()`.

Control flow: Before each test, `storeTestInfo` saves the JUnit `TestInfo`. `getTestName` extracts the method name or returns `unknown`. `uniqueObjectName` truncates the prefix to 50 characters, lowercases it, and appends a zero-padded 10-digit counter.

State and persistence behavior: Runtime state includes per-instance `TestInfo` and static process-wide `OBJECT_COUNTER`. There is no persistence.

Dependencies and integration points: Subclasses can generate bucket, volume, key, or other object names tied to test names while avoiding collisions in the same JVM.

Risks: The static counter is process-local and not reset per test class. Lowercasing and truncation may still produce collisions if many long prefixes share the same first 50 characters, though the counter mitigates within the JVM.

Test signals: Downstream tests rely on names being lowercase, bounded to 60 characters, and unique for repeated calls.
