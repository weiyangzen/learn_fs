# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/ha/SCMRatisServerImpl.java

Purpose: Production Apache Ratis server wrapper for SCM HA, responsible for server construction, request submission, snapshots, peer roles, and dynamic SCM membership.

Important APIs and types: Constructor builds `RaftServer`, `SCMStateMachine`, `RaftGroupId`, and TLS parameters. Static `initialize`, `buildRaftGroupId`, `getSelfPeerId`, and `buildRaftGroup` support SCM init/bootstrap. Runtime APIs include `submitRequest`, `triggerSnapshot`, `addSCM`, `removeSCM`, `getLeader`, `getRatisRoles`, and `triggerNotLeaderException`.

Control flow: Server creation uses the cluster UUID as Raft group id and starts with group id only in bootstrapped mode. `submitRequest` builds a write `RaftClientRequest`, waits with configured timeout, and decodes the reply. Membership changes submit `SetConfigurationRequest` with an updated peer list. Initialization starts a temporary server and waits for leader readiness.

State and persistence behavior: Ratis persists logs and state machine snapshots under configured storage. The implementation tracks client id, monotonically increasing call id, stop state, request timeout, division, and TLS config.

Dependencies and integration points: Integrates `RatisUtil`, `HASecurityUtils`, `StorageContainerManager`, `SCMStateMachine`, SCM node details, and Ratis server APIs.

Risks and test signals: Request timeout is read from a local `OzoneConfiguration` field rather than the passed config, which is worth regression coverage. Hostname strings are intentionally not pre-resolved for peer addresses. Tests should assert group-id derivation, DNS-preserving peer address, timeout validation, setConfiguration error propagation, role formatting, and server close/state-machine close sequencing.
