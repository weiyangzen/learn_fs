# sources/object-store/apache-ozone/hadoop-ozone/tools/src/test/java/org/apache/hadoop/ozone/shell/TestOzoneRatis.java

## Purpose
Tests the Ozone wrapper around Ratis shell, especially local raft-meta-conf rewriting behavior and argument validation.

## Important APIs, types, and functions
Uses `OzoneRatis`, Ratis protobuf `LogEntryProto`, `RaftPeerProto`, `RaftConfigurationProto`, JUnit temp directories, and captured system output/error.

## Control flow
Setup redirects stdout/stderr and creates an `OzoneRatis`. Basic test runs an empty command and checks usage. The raft-meta-conf test writes a protobuf `raft-meta.conf`, invokes `local raftMetaConf` with peer/path args, checks output text, confirms `new-raft-meta.conf` exists, parses it, and validates index and peer fields. Negative tests pass missing/invalid/duplicate peer args and check parse messages.

## State and persistence behavior
Writes temporary Ratis metadata files and generated replacement protobufs. System streams are temporarily replaced.

## Dependencies and integration points
Tests OzoneRatis delegation to Ratis shell local commands and protobuf file compatibility.

## Risks and edge cases
Output message assertions can be brittle across Ratis upgrades. The wrapper does not validate TLS/config integration.

## Test signals
Usage text, generated protobuf index increment, peer id/address/startup role, and exact parse/duplicate error substrings.
