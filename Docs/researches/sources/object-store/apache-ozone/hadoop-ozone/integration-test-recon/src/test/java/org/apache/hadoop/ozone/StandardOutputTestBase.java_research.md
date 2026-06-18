<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test-recon/src/test/java/org/apache/hadoop/ozone/StandardOutputTestBase.java -->
# sources/object-store/apache-ozone/hadoop-ozone/integration-test-recon/src/test/java/org/apache/hadoop/ozone/StandardOutputTestBase.java

Purpose: JUnit 5 base class for tests that need to capture stdout and stderr.

Important APIs: `@BeforeEach setUpStreams` replaces `System.out` and `System.err` with UTF-8 `PrintStream`s backed by byte arrays. `@AfterEach restoreStreams` restores originals. Getter methods expose captured output in default UTF-8 or caller-supplied encodings.

Control flow and integration: `TestNSSummaryAdmin` extends this class to assert CLI output from `OzoneAdmin.execute`.

State and persistence: mutates global JVM streams around each test. No persistence.

Risks and tests: global stream replacement is not safe for parallel tests in the same JVM. Byte arrays are not reset explicitly except by creating a new test instance and before hook; JUnit default per-method lifecycle makes that acceptable. No direct self-test covers this helper.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/integration-test-recon/src/test/java/org/apache/hadoop/ozone/StandardOutputTestBase.java -->
