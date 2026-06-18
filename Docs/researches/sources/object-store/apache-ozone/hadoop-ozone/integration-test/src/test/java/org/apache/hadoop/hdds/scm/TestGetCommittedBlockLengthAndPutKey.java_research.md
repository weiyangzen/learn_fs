# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/hdds/scm/TestGetCommittedBlockLengthAndPutKey.java

## Purpose

`TestGetCommittedBlockLengthAndPutKey` validates SCM/datanode block commit metadata and key finalization responses. It checks committed block length lookup, invalid-block handling, and put-key response semantics in a non-HA cluster.

## Important APIs, Types, And Functions

The abstract test uses `OzoneClient`, `StorageContainerLocationProtocolClientSideTranslatorPB`, `XceiverClientManager`, `ContainerProtocolCalls`, `BlockID`, `ContainerWithPipeline`, `OmKeyArgs`, and key-location helpers. Tests are `tesGetCommittedBlockLength`, `testGetCommittedBlockLengthForInvalidBlock`, and `tesPutKeyResposne`.

## Control Flow

Setup opens client/SCM translator resources. Tests write or allocate blocks, query committed lengths through container protocol paths, assert invalid-block exceptions, and inspect put-key responses after key creation.

## State And Persistence Behavior

Committed block length is persisted in datanode block metadata and exposed through protocol calls. OM key metadata and SCM block/container state are mutated by writes and put-key operations.

## Dependencies And Integration Points

It connects Ozone client writes, SCM allocation, datanode block metadata, container protocol calls, and OM key commit flow.

## Risks And Test Signals

Failures signal mismatches between written chunk lengths and committed block metadata, bad invalid-block error mapping, or regressions in key finalization responses. The typo in method names is harmless but makes name-based test filtering less intuitive.
