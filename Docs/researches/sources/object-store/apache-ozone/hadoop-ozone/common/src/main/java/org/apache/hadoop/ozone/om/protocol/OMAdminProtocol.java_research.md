<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/protocol/OMAdminProtocol.java -->
# sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/protocol/OMAdminProtocol.java

## Purpose

`OMAdminProtocol` defines administrative RPCs for Ozone Manager metadata and maintenance operations.

## Important APIs, Types, And Functions

It extends `Closeable` and declares `getOMConfiguration`, `decommission`, `compactOMDB`, and `triggerSnapshotDefrag`. It is annotated with Kerberos server principal configuration.

## Control Flow, State, And Persistence

This is an RPC interface only. Implementations read OM HA configuration, mutate HA membership during decommission, compact RocksDB column families, or trigger snapshot defragmentation. State changes occur in OM implementation and metadata stores, not here.

## Dependencies And Integration Points

It depends on `OMConfiguration`, `OMNodeDetails`, `OMConfigKeys`, and Hadoop `KerberosInfo`. It integrates with admin clients and server-side OM admin protocol translators.

## Risks And Test Signals

Admin operations are high-impact. Tests should cover Kerberos binding, HA config responses, decommission validation, invalid column family compaction requests, no-wait and wait defrag paths, and close behavior in client translators.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/protocol/OMAdminProtocol.java -->
