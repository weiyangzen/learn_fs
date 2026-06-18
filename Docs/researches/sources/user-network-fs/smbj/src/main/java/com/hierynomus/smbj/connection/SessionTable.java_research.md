# sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/connection/SessionTable.java

Purpose: `SessionTable` maps SMB session IDs to active `Session` objects.

Important APIs and control flow: register, find, remove, active check, and snapshot active sessions are all guarded by a `ReentrantLock`.

State, dependencies, and integration: used by `Connection`, session setup, packet signature/decryption handlers, and close/logoff event handling.

Risks: duplicate registration overwrites silently. Snapshot active sessions may include sessions closing concurrently. Tests should cover lock-protected register/find/remove, active session snapshots, and duplicate-session behavior expectations.
