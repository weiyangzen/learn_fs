<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/conf/DatanodeRatisGrpcConfig.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/conf/DatanodeRatisGrpcConfig.java

## Purpose
`DatanodeRatisGrpcConfig` declares the typed HDDS config bean for datanode Ratis gRPC settings.

## Important APIs, Types, and Functions
It is annotated `@ConfigGroup` with the HDDS datanode Ratis plus Ratis gRPC prefix. It defines config key `hdds.ratis.raft.grpc.flow.control.window`, default `5MB`, type `SIZE`, tags `OZONE`, `CLIENT`, and `PERFORMANCE`, and getter/setter `getFlowControlWindow`/`setFlowControlWindow`.

## Control Flow
There is no runtime algorithm beyond config binding. The annotation processor and Ozone configuration reflection populate the bean from configuration.

## State and Persistence Behavior
The bean stores `flowControlWindow` as an int in bytes. Persistent configuration lives in XML/properties; this object is runtime state.

## Dependencies and Integration Points
It depends on HDDS config annotations, `RatisHelper.HDDS_DATANODE_RATIS_PREFIX_KEY`, and Ratis `GrpcConfigKeys.PREFIX`. It feeds datanode Ratis gRPC setup.

## Risks and Test Signals
Risks include int overflow for large sizes, setting a window smaller than chunk size, and prefix/key duplication mismatches. Test signals include generated config docs, config binding tests, and datanode Ratis write throughput with large chunks.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/conf/DatanodeRatisGrpcConfig.java -->
