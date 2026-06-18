<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/S3SecretValue.java -->
# sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/S3SecretValue.java

## Purpose

`S3SecretValue` is the persisted value for an S3 access ID and secret pair, historically named with `kerberosID`.

## Important APIs, Types, And Functions

The class exposes `getCodec`, factory methods `of`, `deleted`, getters for Kerberos/access ID, secret, deletion flag, and transaction log index, `fromProtobuf`, `getProtobuf`, `equals`, `hashCode`, and `toString`.

## Control Flow, State, And Persistence

Instances are immutable. `CODEC` persists through the `S3Secret` protobuf. `deleted()` returns a tombstone-like value with an empty secret and deletion flag set, but `getProtobuf` does not encode `isDeleted` or `transactionLogIndex`; `fromProtobuf` recreates a non-deleted value with index zero.

## Dependencies And Integration Points

It depends on HDDS DB codecs and `OzoneManagerProtocolProtos.S3Secret`. It integrates with OM S3 secret tables, tenant access ID assignment, S3 gateway authentication, and `OzoneManagerProtocol.getS3Secret`/`setS3Secret`.

## Risks And Test Signals

`toString()` prints the secret, which is sensitive. Deletion/index fields are not preserved by protobuf conversion. Tests should cover secret persistence, tombstone semantics in the surrounding table code, equality including deletion/index, and log redaction expectations.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/S3SecretValue.java -->
