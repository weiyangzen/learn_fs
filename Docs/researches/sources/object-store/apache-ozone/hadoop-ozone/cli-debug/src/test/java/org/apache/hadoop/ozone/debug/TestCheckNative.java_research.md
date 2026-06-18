# sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/test/java/org/apache/hadoop/ozone/debug/TestCheckNative.java

Purpose: `TestCheckNative` verifies `ozone debug checknative` output for native library availability.

Important APIs and types: It uses `OzoneDebug`, `GenericTestUtils.PrintStreamCapturer`, `ROCKS_TOOLS_NATIVE_PROPERTY`, JUnit conditional annotations, and AssertJ.

Control flow: Each test captures stdout, executes `new OzoneDebug().getCmd().execute("checknative")`, normalizes repeated spaces, and checks expected library lines. One test runs when rocks-tools native is not enabled; the other runs when the system property is true.

State and persistence behavior: No persistence. It mutates only captured process stdout and closes the capturer after each test.

Dependencies and integration points: It is a CLI integration test for the debug command registry and native-check reporting.

Risks: The assertions encode expected false values for Hadoop, ISA-L, and OpenSSL in the test environment. Environment-specific native library loading can change test applicability.

Test signals: Required signals are header text and exact `rocks-tools` boolean matching the system property condition.
