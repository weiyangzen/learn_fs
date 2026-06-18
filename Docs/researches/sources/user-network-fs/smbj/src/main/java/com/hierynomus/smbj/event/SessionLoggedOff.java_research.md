# sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/event/SessionLoggedOff.java

Purpose: `SessionLoggedOff` signals that a session has logged off.

Important APIs and control flow: it only passes the session ID to `SessionEvent`.

State, dependencies, and integration: handled by `Connection` to remove sessions from `SessionTable`.

Risks: cleanup depends on event publication during session close. Tests should cover session logoff event leading to session table removal.
