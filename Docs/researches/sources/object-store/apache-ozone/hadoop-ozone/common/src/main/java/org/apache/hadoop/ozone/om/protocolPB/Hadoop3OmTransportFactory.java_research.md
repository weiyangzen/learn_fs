<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/protocolPB/Hadoop3OmTransportFactory.java -->
# sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/protocolPB/Hadoop3OmTransportFactory.java

## Purpose

`Hadoop3OmTransportFactory` creates Hadoop RPC-backed OM transports.

## Important APIs, Types, And Functions

It implements `OmTransportFactory.createOmTransport(ConfigurationSource, UserGroupInformation, String)` and returns a new `Hadoop3OmTransport`.

## Control Flow, State, And Persistence

The factory has no state. Each invocation constructs a transport configured with the supplied configuration, user, and OM service ID.

## Dependencies And Integration Points

It depends on `OmTransportFactory`, `Hadoop3OmTransport`, configuration, UGI, and IO exceptions. It integrates with the transport factory selection path used by OM protocol clients.

## Risks And Test Signals

Factory behavior is simple, so most risk is constructor propagation. Tests should cover default factory selection, HA service ID propagation, UGI propagation, and startup failures for invalid follower-read consistency config.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/protocolPB/Hadoop3OmTransportFactory.java -->
