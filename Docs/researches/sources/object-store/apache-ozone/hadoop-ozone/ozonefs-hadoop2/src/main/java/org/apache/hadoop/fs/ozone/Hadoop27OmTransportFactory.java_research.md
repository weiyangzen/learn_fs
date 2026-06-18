<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozonefs-hadoop2/src/main/java/org/apache/hadoop/fs/ozone/Hadoop27OmTransportFactory.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozonefs-hadoop2/src/main/java/org/apache/hadoop/fs/ozone/Hadoop27OmTransportFactory.java

## Purpose
Hadoop 2.7 OM transport factory that creates RPC transports with failover support.

## Important APIs, types, and functions
Implements `OmTransportFactory`. `createOmTransport` takes a `ConfigurationSource`, `UserGroupInformation`, and OM service ID, and returns a new `Hadoop27RpcTransport`.

## Control flow
No branching beyond construction. All transport behavior is delegated to `Hadoop27RpcTransport`.

## State and persistence behavior
The factory is stateless.

## Dependencies and integration points
Used where Ozone client code discovers an OM transport factory on a Hadoop 2 classpath. It bridges Ozone OM protocol abstractions to the Hadoop 2 shaded RPC implementation.

## Risks and test signals
Risk is limited to service discovery and constructor compatibility. Tests should verify client initialization with Hadoop 2 selects this factory and can submit OM requests through the returned transport.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozonefs-hadoop2/src/main/java/org/apache/hadoop/fs/ozone/Hadoop27OmTransportFactory.java -->
