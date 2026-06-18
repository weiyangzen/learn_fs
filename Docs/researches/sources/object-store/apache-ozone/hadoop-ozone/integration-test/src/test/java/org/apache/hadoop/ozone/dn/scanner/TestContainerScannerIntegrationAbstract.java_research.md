# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/dn/scanner/TestContainerScannerIntegrationAbstract.java

Purpose: Shared integration-test harness for datanode container scanner tests. It builds a one-datanode cluster, creates object store fixtures, writes/open/closes containers, waits for SCM state, and exposes helpers for checksum and corruption assertions.

Important APIs, types, and functions: Provides `buildCluster`, `pauseScanner`, `resumeScanner`, `waitForScmToSeeReplicaState`, `waitForScmToCloseContainer`, `getDnContainer`, `containerChecksumFileExists`, `writeDataThenCloseContainer`, `writeDataToOpenContainer`, `closeContainerAndWait`, `getTestData`, `getContainerReplica`, `readFromCorruptedKey`, `getContainerLogCapturer`, `getConf`, and `getDatanode`. Uses `MiniOzoneCluster`, `OzoneClient`, `ObjectStore`, `OzoneBucket`, `OzoneContainer`, `ContainerManager`, `ContainerReplica`, and `ContainerMerkleTreeTestUtils`.

Control flow: `buildCluster` configures one-second container reports, zero minimum scan gap, starts a one-DN mini cluster, waits for a Ratis ONE pipeline, creates a volume/bucket, and stores static handles. Write helpers create keys with `TestHelper.createKey`, write data larger than one chunk, close containers through SCM, wait until the datanode reports local closure, and wait until SCM sees a non-zero data checksum. Open-container helper writes without closing. Read helper attempts a key read and expects an `IOException`.

State and persistence behavior: Maintains static cluster/client/store/bucket state shared by subclasses. Writes real key/container data and relies on container close to generate persisted checksum tree files. Pause/resume directly affects the datanode `OzoneContainer` scrub scheduler.

Dependencies and integration points: Centralizes cluster setup for background and on-demand scanner tests, SCM state polling, Ozone object writes/reads, and checksum file checks.

Risks: Static shared fixtures mean subclasses must not run in ways that conflict. Wait timeouts are tuned for a single-datanode mini cluster. The log capturer captures broad Log4j output because targeted Log4j2 capture is unavailable.

Test signals: Helpers assert single-datanode replica counts, non-zero closed checksums, expected read failures from corrupted keys, and SCM/container state convergence.
