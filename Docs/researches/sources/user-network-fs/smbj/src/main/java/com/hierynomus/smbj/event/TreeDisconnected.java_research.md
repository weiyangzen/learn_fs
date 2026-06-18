# sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/event/TreeDisconnected.java

Purpose: `TreeDisconnected` signals that a tree/share connection was disconnected within a session.

Important APIs and control flow: extends `SessionEvent` and adds `treeId`.

State, dependencies, and integration: consumed by components that track per-session tree connections.

Risks: unlike `SessionEvent`, equality/hash code do not include `treeId` because it inherits the base implementation. Tests should confirm whether this is intentional, especially when multiple tree IDs disconnect under one session.
