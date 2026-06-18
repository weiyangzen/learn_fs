# sources/object-store/apache-ozone/hadoop-ozone/common/src/test/java/org/apache/hadoop/ozone/TestOmUtils.java

Purpose: unit tests for `OmUtils`, covering OM directory creation, HA service discovery, OM address parsing, listener-node filtering, transaction/object ID epoch encoding, and follower-read request classification.

Important APIs/types/functions: exercises `createOMDir`, `getOmHAAddressesById`, `getOzoneManagerServiceId`, `getOmHostsFromConfig`, `getOmAddress`, `getListenerOMNodeIds`, `getActiveNonListenerOMNodeIds`, `getOMEpoch`, `addEpochToTxId`, `getObjectIdFromTxId`, `shouldSendToFollower`, and `isReadOnly`. It also asserts `MAX_TRXN_ID` equals `2^54 - 2`.

Control flow and state: tests build temporary directories and in-memory `OzoneConfiguration` instances. HA service ID selection prefers `ozone.om.internal.service.id`, rejects mismatches and ambiguous multi-service config, and returns null for non-HA. Object IDs encode epoch in the top two bits and transaction ID shifted by eight bits.

Dependencies and integration points: integrates with `OMConfigKeys`, `ConfUtils`, `OzoneManagerProtocolProtos.OMRequest`, `GenericTestUtils.LogCapturer`, and JUnit temp directories. Follower-read tests iterate every protobuf command enum to ensure new commands are categorized.

Risks and test signals: catches filesystem permission regressions, HA config ambiguity, listener OM inclusion bugs, transaction ID overflow, and unsafe follower routing. The enum coverage test is a strong signal for future protobuf additions because uncategorized command types log an error and fail the test.
