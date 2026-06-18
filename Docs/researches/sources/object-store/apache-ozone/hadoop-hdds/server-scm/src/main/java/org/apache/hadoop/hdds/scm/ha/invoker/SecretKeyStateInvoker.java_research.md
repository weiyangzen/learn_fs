# sources/object-store/apache-ozone/hadoop-hdds/server-scm/src/main/java/org/apache/hadoop/hdds/scm/ha/invoker/SecretKeyStateInvoker.java

Purpose: Generated invoker/proxy for HA replication of SCM secret-key state updates.

Important APIs and types: `ReplicateMethod` contains `updateKeys(List)`. Proxy read methods `getCurrentKey`, `getKey`, and `getSortedKeys` call the local implementation; `reinitialize` is local; `updateKeys` is replicated direct.

Control flow: Replicated updates are encoded as list arguments and submitted to Ratis. Local dispatch returns managed secret keys or lists through `SCMRatisResponse` when invoked from a committed log entry.

State and persistence behavior: The invoker does not store keys; the underlying `SecretKeyState` tracks current/sorted managed secret keys and is reinitialized after snapshot install.

Dependencies and integration points: Uses `ManagedSecretKey` codec and participates in `SCMStateMachine.reinitialize` when secret keys are fetched from the leader.

Risks and test signals: List serialization assumes all keys share the supported managed-key type. Tests should cover update replication, key lookup pass-through, sorted key list round trip, reinitialize after checkpoint, and error translation.
