<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/RepeatedOmKeyInfo.java -->
# sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/RepeatedOmKeyInfo.java

## Purpose

`RepeatedOmKeyInfo` stores multiple deleted incarnations of the same key name in OM's deleted table. It supports GDPR-style verification and quota accounting when the same URI is recreated and deleted repeatedly.

## Important APIs, Types, And Functions

Important methods are `getCodec(boolean ignorePipeline)`, constructors, `addOmKeyInfo`, `getOmKeyInfoList`, `cloneOmKeyInfoList`, `getTotalSize`, `builderFromProto`, `getFromProto`, `getProto`, `getBucketId`, and `copyObject`. The builder stores the key-info list and bucket ID.

## Control Flow, State, And Persistence

The class persists through delegated codecs backed by `RepeatedKeyInfo` protobuf. Two codecs differ by whether pipeline data is compacted/ignored. `getProto` clones the key list before serialization to avoid concurrent modification, serializes each `OmKeyInfo`, and records `bucketId`.

## Dependencies And Integration Points

It depends on HDDS DB codecs, `OmKeyInfo`, `ClientVersion`, `RepeatedKeyInfo`, `KeyInfo`, and Apache Commons `ImmutablePair`. It integrates with OM deleted-key tables, key deletion services, quota repair, and snapshot/deleted data cleanup.

## Risks And Test Signals

The returned `getOmKeyInfoList()` is mutable, and builder can build with null lists. Tests should cover codec round trips with and without compact pipeline data, total size accounting, bucket ID preservation, concurrent serialization safety, and copy behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/RepeatedOmKeyInfo.java -->
