# sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/connection/packet/AbstractIncomingPacketHandler.java

Purpose: `AbstractIncomingPacketHandler` provides chain-of-responsibility plumbing for incoming SMB packet handlers.

Important APIs and control flow: `handle` checks `canHandle`; if true, calls `doHandle`, otherwise delegates to `next`. `setNext` stores and returns this handler to enable fluent chain construction.

State, dependencies, and integration: state is the next handler reference. `Connection.init` builds the incoming chain from these handlers.

Risks: if `next` is null and `canHandle` is false, handling throws `NullPointerException`; the chain relies on a dead-letter tail. Tests should cover delegation order and terminal behavior.
