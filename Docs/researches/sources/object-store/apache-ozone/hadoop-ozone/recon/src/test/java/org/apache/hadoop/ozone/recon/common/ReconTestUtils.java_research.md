# sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/common/ReconTestUtils.java

Purpose: This small test utility class centralizes creation of `SCMNodeDetails` for Recon-oriented tests. It supplies a deterministic Recon node id and datanode protocol server address.

Important APIs/types/functions: The exported API is `ReconTestUtils.getReconNodeDetails()`. It uses `SCMNodeDetails.Builder`, `setSCMNodeId`, `setDatanodeProtocolServerAddress`, and `InetSocketAddress.createUnresolved("127.0.0.1", 9888)`. The private constructor prevents instantiation.

Control flow: Calling `getReconNodeDetails` creates a new builder, sets `SCMNodeId` to `Recon`, sets the datanode protocol server address, and returns `builder.build()`.

State and persistence behavior: There is no persistence or shared mutable state. Each call returns a newly built value object. The address is unresolved to avoid DNS/network dependency during tests.

Dependencies and integration points: The helper is intended for Recon tests that need SCM node details without standing up a full SCM service. It integrates with HDDS SCM HA metadata types and gives tests a consistent Recon identity.

Risks: The fixed port `9888` and id `Recon` may conflict with tests that need multi-node uniqueness if reused blindly. The helper only sets the datanode protocol address, not the full matrix of SCM service endpoints.

Test signals: This is a helper rather than a test. Its correctness signal is deterministic construction of an `SCMNodeDetails` instance suitable for test injection.
