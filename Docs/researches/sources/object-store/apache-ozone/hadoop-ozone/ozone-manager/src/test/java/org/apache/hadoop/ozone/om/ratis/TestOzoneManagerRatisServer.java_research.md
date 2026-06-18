# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/ratis/TestOzoneManagerRatisServer.java

Purpose: unit/integration-style tests for single-node `OzoneManagerRatisServer` startup, peer address generation, snapshot info loading, read-only command categorization, and Raft group ID derivation.

Important APIs/types: `OzoneManagerRatisServer`, `OMNodeDetails`, `OMStorage`, `OMCertificateClient`, `SecurityConfig`, `OmMetadataManagerImpl`, `TransactionInfo`, `SnapshotInfo`, `RaftGroupId`, and `OmUtils.isReadOnly`.

Control flow: setup disables system exit, creates temporary metadata/configuration, mocks OM storage and manager, constructs certificate client, starts a single-node OM Ratis server, and teardown stops it. Tests assert running lifecycle state, verify `createRaftPeer` preserves configured hostname strings, manually update transaction info then restart to ensure snapshot info is loaded, loop every OM command type through `OmUtils.isReadOnly` to detect uncategorized enum values, and verify default/custom OM service IDs map deterministically to 16-byte Raft group IDs.

State and persistence behavior: the metadata manager persists `TRANSACTION_INFO_KEY`, which is used to seed last-applied term/index on server restart. Ratis server lifecycle state is observable through `getServerState`.

Dependencies and integration points: integrates Ratis server construction, OM node details, certificate/security config, OM metadata DB, command classification, and Raft identity.

Risks: binds to local host/network behavior and real server startup. Hostname preservation test uses a synthetic DNS name and only checks formatting, not live resolution. Snapshot restart test mutates DB directly.

Test signals: verifies server starts, peer addresses are not pre-resolved, last-applied term/index survives restart, every command type is categorized, and service ID determines Raft group UUID.
