# sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/event/SessionEvent.java

Purpose: `SessionEvent` is the package-private base for events tied to an SMB session ID.

Important APIs and control flow: constructor stores `sessionId`; getter exposes it; equality and hash code compare exact event class and session ID.

State, dependencies, and integration: extended by `SessionLoggedOff` and `TreeDisconnected`.

Risks: exact-class equality means different session event subtypes with the same ID are intentionally not equal. Tests should verify equality semantics and event consumer matching.
