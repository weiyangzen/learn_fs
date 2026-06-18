# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/ScmUtils.java

Purpose: Static SCM utilities for bind-address resolution, peer-removal policy, container report queue creation, and certificate-signing checks during CA rotation.

Important APIs and types: Includes SCM block/client/datanode address helpers, address-key helpers, `shouldRemovePeers`, `initContainerReportQueue`, `getContainerReportConfPrefix`, and `checkIfCertSignRequestAllowed`.

Control flow: Address helpers build service/node-suffixed config keys, prefer bind host keys, parse deprecated combined address keys for ports, log warnings, and build socket addresses. Queue initialization creates one bounded queue per configured event thread. Certificate checks throw specific `SCMException` codes during rotation/post-rotation.

State and persistence behavior: Stateless; reads configuration and root CA rotation state.

Dependencies and integration points: Used by SCM protocol servers, container report handling, placement policy, HA config suffixes, and security certificate flows.

Risks: Deprecated address keys can override port behavior. Queue sizes affect heartbeat/report backpressure. Rotation checks must be applied consistently.

Test signals: Verify config precedence, warning paths, peer-removal booleans, queue count/size, and CA rotation exception codes.
