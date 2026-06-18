# sources/object-store/apache-ozone/hadoop-ozone/cli-debug/src/test/java/org/apache/hadoop/ozone/debug/kerberos/TestOzoneDebugKerberos.java

Purpose: `TestOzoneDebugKerberos` validates the `ozone debug kerberos` diagnostics and principal translation command surfaces.

Important APIs and types: It uses `OzoneDebug`, `GenericTestUtils` output capturers, AssertJ, and system property `java.security.krb5.conf`.

Control flow: Each test captures stdout/stderr, executes either `kerberos diagnose` or `kerberos translate-principal testuser/host@EXAMPLE.COM`, normalizes spaces, and asserts headers, sections, summary counters, and return codes. The failure scenario sets `java.security.krb5.conf` to an invalid path to force the JVM Kerberos probe to fail.

State and persistence behavior: No persistence. The test temporarily mutates a JVM system property and clears it after each test.

Dependencies and integration points: It covers debug command registration plus environmental Kerberos probes and auth-to-local mapping behavior.

Risks: Results depend on local Kerberos environment; translation may pass or fail, so the test accepts either but requires return code consistency. Diagnose success only requires nonnegative return code.

Test signals: Presence of all diagnostic sections, `FAIL` on invalid krb5 config, and translation summary with pass/fail return-code alignment.
