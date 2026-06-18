<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/test/java/org/apache/hadoop/hdds/scm/cli/cert/TestCleanExpiredCertsSubcommand.java -->
# sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/test/java/org/apache/hadoop/hdds/scm/cli/cert/TestCleanExpiredCertsSubcommand.java

Purpose: Tests the certificate cleanup CLI output when SCM security removes expired certificates.

Important APIs and types: `CleanExpiredCertsSubcommand`, mocked `SCMSecurityProtocol`, `CertificateInfo`, serial number, captured stdout/stderr, Mockito, and AssertJ.

Control flow: Setup mocks the security protocol and redirects output. The test builds a certificate info object, has `removeExpiredCertificates()` return it in a list, runs the command, and asserts the serial/certificate info appears in CLI output.

State and persistence behavior: No real certificate store is mutated; persistence is represented by the mocked security protocol return value.

Dependencies and integration points: Exercises the SCM security admin command's formatting against the protocol contract used to remove expired certs.

Risks: Coverage shown is a positive one-certificate path; empty results, multiple certificates, and protocol failures need separate coverage.

Test signals: Output contains the removed certificate's serial/info and streams are restored after test.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/cli-admin/src/test/java/org/apache/hadoop/hdds/scm/cli/cert/TestCleanExpiredCertsSubcommand.java -->
