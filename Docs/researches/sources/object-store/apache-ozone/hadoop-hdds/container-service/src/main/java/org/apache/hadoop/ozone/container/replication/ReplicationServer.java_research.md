# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/replication/ReplicationServer.java

Purpose: owns the dedicated datanode-to-datanode gRPC server used for container replication.

Important APIs and functions: the constructor stores security, controller, importer, port, builds a bounded fixed-size `ThreadPoolExecutor`, and calls `init`. `init` creates a `GrpcReplicationService`, installs a tracing interceptor, configures max inbound message size, attaches the executor, and optionally configures mutual TLS with key/trust managers, protocols, ciphers, and provider. `start` starts the gRPC server and records the actual bound port. `stop` shuts down executor and server with bounded waits. `setPoolSize` dynamically resizes the executor. Nested `ReplicationConfig` defines stream limit, queue limit, port, and out-of-service scaling factor with validation.

Control flow and state: server lifecycle is explicit; `OzoneContainer.start` starts it before exposing the port in `DatanodeDetails`. The executor queue is bounded by config, and rejected tasks rely on gRPC/executor behavior. Out-of-service scaling is exposed to supervisor and other components via `ReplicationConfig`.

Dependencies and integration: integrates `ContainerController`, `ContainerImporter`, `OnDemandContainerReplicationSource`, gRPC Netty, Ratis tracing, and datanode security.

Risks and test signals: TLS misconfiguration fails server construction, and shutdown order can leave active streams interrupted. Tests should cover plaintext/TLS init, dynamic port binding, queue limit behavior, invalid config clamping, pool resizing, and graceful stop under active streams.
