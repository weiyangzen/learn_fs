# sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/connection/packet/DeadLetterPacketHandler.java

Purpose: `DeadLetterPacketHandler` is the terminal sink for packets rejected or unhandled by the incoming chain.

Important APIs and control flow: `canHandle` always returns true and `doHandle` logs a warning without throwing.

State, dependencies, and integration: used as the final handler after SMB1 handling in `Connection`.

Risks: invalid packets may only be logged, leaving request promises unresolved if a prior handler did not deliver an error. Tests should verify dead-letter paths for unknown responses and assess whether outstanding requests time out.
