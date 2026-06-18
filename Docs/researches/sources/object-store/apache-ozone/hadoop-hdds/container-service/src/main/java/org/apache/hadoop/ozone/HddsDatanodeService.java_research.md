# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/HddsDatanodeService.java

## Purpose
Main Ozone datanode service entry point and service plugin that initializes identity, security, layout storage, reconfiguration, RPC/HTTP servers, plugins, metrics, Ratis/container state machine, and shutdown behavior.

## Important APIs, Types, And Functions
Implements `Callable<Void>` and Hadoop `ServicePlugin`. Key APIs include `main`, `call`, `start(Object)`, `start(OzoneConfiguration)`, `start`, `stop`, `join`, `close`, `initializeCertificateClient`, `saveNewCertId`, and reconfiguration callbacks for block deletion, replication streams, and SCM node membership.

## Control Flow
Startup activates Ozone configuration, initializes metrics, loads or creates datanode details, validates host/IP, performs Kerberos login when security is enabled, initializes datanode layout storage, certificate and secret-key clients, builds `ReconfigurationHandler`, constructs `DatanodeStateMachine`, starts HTTP and client RPC servers, loads plugins, starts the state-machine daemon, optionally starts standalone Ratis for tests, and registers the MXBean. Shutdown stops plugins, reconfiguration handler, state machine, HTTP/RPC servers, JMX, Ratis metric reporters, and secret key client.

## State And Persistence
Persistent state includes the datanode ID file, layout storage VERSION metadata, certificate serial ID persisted through `persistDatanodeDetails`, and service endpoints in datanode details. In-memory state includes config, security clients, state machine, plugin list, MXBean name, reconfiguration handler, SCM service ID, and stop flag.

## Dependencies And Integration Points
Integrates with HDDS/Ozone CLI, security, SCM security protocol, datanode state machine, volume checking, disk balancer, RPC/HTTP servers, Ozone admins, tracing reconfiguration, Ratis metrics, service plugins, and shutdown hooks.

## Risks
Startup has many partial-failure boundaries: HTTP failure is logged but not fatal, while security/authentication and layout failures are fatal. Reconfiguring SCM nodes is allowed only in RUNNING state and partial add/remove results intentionally return effective node IDs. Stop is guarded by `AtomicBoolean`, but `close` is separate. Certificate persistence failure terminates the datanode.

## Test Signals
Signals include secure and insecure startup, identity persistence, Kerberos/certificate recovery, RPC/HTTP port publication, plugin lifecycle, state-machine daemon operation, dynamic reconfiguration of delete threads/replication streams/SCM nodes, MXBean registration, and orderly shutdown.
