# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/client/rpc/TestCloseContainerHandlingByClient.java

## Purpose
This abstract `NonHATests.TestCase` verifies that the Ozone client handles close-container exceptions during normal RATIS key writes. It focuses on data length, block-location metadata, and readback after a container is closed between writes or before stream close.

## Important APIs, types, and functions
The class depends on an externally supplied `cluster()` from the non-HA test harness. It uses `MiniOzoneCluster`, `ObjectStore`, `OzoneOutputStream`, `KeyOutputStream`, `OzoneInputStream`, `OmKeyArgs`, `OmKeyInfo`, `OmKeyLocationInfo`, `RatisReplicationConfig`, and `StandaloneReplicationConfig`. Helper methods wrap `TestHelper.waitForContainerClose`, `TestHelper.createKey`, and `TestHelper.validateData`.

## Control flow
`init()` reads configured chunk and block sizes, creates a client, volume, and bucket, and seeds a random string for deterministic data. Tests write one or more chunks/blocks, force the current container closed with `waitForContainerClose(key)`, then continue writing or close the stream. After close, they query OM key metadata via `lookupKey` and validate data by reading the key.

The scenarios cover flush-and-close after a mid-stream close, close consistency when no extra data is written, several multi-block preallocation and partial-buffer cases, a RATIS factor-three path, and a larger two-write case. Multi-block tests inspect key location counts and each `OmKeyLocationInfo` length to verify that remaining buffered data is copied into newly allocated blocks when the original container closes.

## State and persistence behavior
The state under test includes preallocated stream entries, OM key size, key location versions, block lengths, and persisted object bytes. Container closure forces the client to discard or bypass failing block streams and allocate new blocks, while OM should reflect only successfully committed data. The tests assert both metadata size and full byte equality.

## Dependencies and integration points
This file integrates client-side block stream recovery, SCM container closure, OM key lookup, RATIS replication config, and the non-HA test harness. It is abstract because concrete subclasses provide the cluster topology.

## Risks and test signals
The class uses replication config values in `OmKeyArgs` that are not always the same as the create-key type in every test, so the main signal is OM lookup and key data rather than replication assertion. The strongest regression indicators are incorrect `dataSize`, wrong number of location infos, missing reallocated block data, or readback mismatch after a container close.
