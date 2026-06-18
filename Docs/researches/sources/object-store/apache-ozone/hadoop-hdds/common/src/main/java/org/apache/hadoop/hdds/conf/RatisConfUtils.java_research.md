## sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/conf/RatisConfUtils.java

Purpose: helper namespace for Ratis configuration adjustments.

Important API: `RatisConfUtils.Grpc.setMessageSizeMax(RaftProperties,int)` validates a desired maximum and sets Ratis gRPC max message size to that value plus 1 MB, preserving a required gap for RATIS-2135.

Control flow: asserts max is positive and at least the current Ratis log appender buffer byte limit, then writes `GrpcConfigKeys.setMessageSizeMax`. State/persistence: mutates caller-provided `RaftProperties`; no class state.

Dependencies: Ratis config keys, `RaftProperties`, `Preconditions`, `SizeInBytes`. Integration points: datanode/server Ratis property setup. Risks: assertion failures at startup if max is under buffer limit; the extra 1 MB is protocol/config compatibility-sensitive. Test signals: below/above buffer-limit cases, exact gap setting, and positive validation.
