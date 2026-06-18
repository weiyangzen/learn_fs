<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozonefs-hadoop2/src/main/java/org/apache/hadoop/fs/ozone/Hadoop27RpcTransport.java -->
# sources/object-store/apache-ozone/hadoop-ozone/ozonefs-hadoop2/src/main/java/org/apache/hadoop/fs/ozone/Hadoop27RpcTransport.java

## Purpose
Hadoop 2-compatible OM protobuf RPC transport with leader/follower failover support.

## Important APIs, types, and functions
Implements `OmTransport`. Constructor configures Hadoop protobuf RPC engine, creates `HadoopRpcOMFailoverProxyProvider`, reads follower-read and failover settings, builds `HadoopRpcOMFollowerReadFailoverProxyProvider`, and creates an `OzoneManagerProtocolPB` proxy. `submitRequest`, `getDelegationTokenService`, and `close` implement the transport API.

## Control flow
`submitRequest` sends the protobuf request with a null controller. Non-leader `ServiceException`s are converted into a generic leader-connection `IOException`; other service exceptions are converted through Hadoop protobuf helper. `close` closes the follower-read provider when present, otherwise the base failover provider.

## State and persistence behavior
Local state is the RPC proxy and failover providers. Persistent metadata changes depend on the OM request payload.

## Dependencies and integration points
This class depends on relocated Hadoop 2 IPC packages (`org.apache.hadoop.ipc_`), Ozone OM failover providers, follower-read consistency config, protobuf OM request/response types, and Ratis leader semantics.

## Risks and test signals
The main risks are exception translation losing detail, `getDelegationTokenService` returning null, and follower-read consistency defaults failing to parse. Tests should submit read and write requests through HA configurations, verify failover behavior, and exercise not-leader exceptions on Hadoop 2.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-ozone/ozonefs-hadoop2/src/main/java/org/apache/hadoop/fs/ozone/Hadoop27RpcTransport.java -->
