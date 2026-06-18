## sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/protocol/commands/ReregisterCommand.java

Purpose: `ReregisterCommand` tells a datanode to register with SCM again.

Important APIs and types: it extends `SCMCommand<ReregisterCommandProto>`, reports type `reregisterCommand`, returns a default empty `ReregisterCommandProto`, and overrides `getId()`.

Control flow and state: unlike most `SCMCommand` subclasses, `getId()` always returns `0` with a comment that id handling is not implemented for this command. `getProto()` emits no command id. The inherited term, encoded token, and deadline methods still exist and are included in `toString()`.

Persistence and integration: this is transient command signaling. It integrates with datanode endpoint state machines that need to restart registration after SCM-side state changes or rejected heartbeats. There is no local persistence in the class.

Risks and test signals: the constant id means command status tracking cannot distinguish multiple reregister commands by id. If a generic command queue assumes non-zero ids, this command is an exception. No direct tests are present in this subset; heartbeat and registration tests using `ScmTestMock` can indirectly exercise reregistration when SCM command responses include this type.
