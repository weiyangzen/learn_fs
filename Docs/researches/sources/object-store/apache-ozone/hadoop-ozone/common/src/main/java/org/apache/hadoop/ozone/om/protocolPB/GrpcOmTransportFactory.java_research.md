<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/protocolPB/GrpcOmTransportFactory.java -->
# sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/protocolPB/GrpcOmTransportFactory.java

## Purpose

`GrpcOmTransportFactory` creates gRPC-backed OM transports.

## Important APIs, Types, And Functions

It implements `OmTransportFactory.createOmTransport(ConfigurationSource, UserGroupInformation, String)` and returns a new `GrpcOmTransport`.

## Control Flow, State, And Persistence

The factory is stateless. Each call constructs a transport, which immediately initializes its failover provider and gRPC channels.

## Dependencies And Integration Points

It depends on `OmTransportFactory`, `GrpcOmTransport`, configuration, UGI, and IO exceptions. It is selected by the configurable OM transport factory mechanism.

## Risks And Test Signals

Failures are constructor/channel setup failures from `GrpcOmTransport`. Tests should cover factory selection, service ID propagation, UGI propagation, and error handling when gRPC endpoints are misconfigured.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/protocolPB/GrpcOmTransportFactory.java -->
