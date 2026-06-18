<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/security/x509/certificate/client/TestRootCaRotationPoller.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/security/x509/certificate/client/TestRootCaRotationPoller.java

Purpose: validates client-side polling for root CA rotation, ensuring processors are invoked only when SCM returns previously unknown root CA certificates and that retry behavior works after renewal-related failures.

Important APIs/types/functions: `RootCaRotationPoller`, `SCMSecurityProtocolClientSideTranslatorPB.getAllRootCaCertificates`, `CertificateCodec.getPEMEncodedString`, `SecurityConfig`, `SelfSignedCertificate`, `RootCARotationProcessor`, `pollRootCas`, `addRootCARotationProcessor`, and `setCertificateRenewalError`.

Control flow: setup initializes a mocked SCM security client, a polling interval, and log capture. The first test returns only the already-known root CA and verifies a registered processor is not called. The second test returns a known plus new root CA and checks the processor observes the new set. The retry test has the processor mark renewal error on first processing, then invokes polling again and checks log output for failure followed by success.

State and persistence behavior: poller state is in memory: known certificate set, processor list, and error flags. Certificates are generated as self-signed root CAs and serialized through PEM strings returned by the mocked SCM client. No disk state is created by these tests.

Dependencies and integration points: integrates mocked SCM security RPC, certificate serialization, self-signed root certificate generation, async future/timeout behavior, `AtomicBoolean`, and log capture.

Risks: polling and processor invocation may be asynchronous depending on implementation; timeout assertions can be sensitive to executor timing. Log-message assertions are brittle but capture important retry semantics.

Test signals: verifies no callback for unchanged roots, callback for new roots, processor certificate-set size, caught renewal error logging, and successful subsequent processing.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/test/java/org/apache/hadoop/hdds/security/x509/certificate/client/TestRootCaRotationPoller.java -->
