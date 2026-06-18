<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/protocolPB/Hadoop3OmTransport.java -->
# sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/protocolPB/Hadoop3OmTransport.java

## Purpose

`Hadoop3OmTransport` is the Hadoop RPC implementation of `OmTransport` with OM HA failover and optional follower-read routing.

## Important APIs, Types, And Functions

Important methods are the constructor, `submitRequest`, `getDelegationTokenService`, testing getters for failover providers, and `close`. The constructor configures protobuf RPC engine, leader failover provider, follower-read proxy provider, max failovers, and default read-consistency modes.

## Control Flow, State, And Persistence

`submitRequest` delegates one `OMRequest` to the protobuf RPC proxy. It unwraps `ServiceException` into remote exceptions, and maps unresolved not-leader handling to a generic leader connection failure. The transport holds runtime proxy/failover state; no OM metadata is persisted here.

## Dependencies And Integration Points

It depends on Hadoop RPC/protobuf engine, Ozone configuration keys, OM failover providers, `ReadConsistency`, OM protobuf protocol, UGI, and delegation token text. It is the default full-featured client transport used by OM protocol translators.

## Risks And Test Signals

Configuration strings are converted with `ReadConsistency.valueOf`, so invalid values fail at startup. Tests should cover leader failover, follower-read enabled/disabled routing, read consistency defaults, remote exception unwrapping, not-leader handling, delegation token service updates, and close behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/protocolPB/Hadoop3OmTransport.java -->
