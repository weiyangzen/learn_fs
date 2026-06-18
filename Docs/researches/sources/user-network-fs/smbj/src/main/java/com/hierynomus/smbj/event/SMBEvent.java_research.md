# sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/event/SMBEvent.java

Purpose: `SMBEvent` is the marker interface for events published through SMBJ's event bus.

Important APIs and control flow: no methods; it establishes a common message type for the bus.

State, dependencies, and integration: implemented by connection, session, and tree events.

Risks: marker-only design puts schema validation on individual event classes. Tests should focus on bus publication and handler subscription behavior.
