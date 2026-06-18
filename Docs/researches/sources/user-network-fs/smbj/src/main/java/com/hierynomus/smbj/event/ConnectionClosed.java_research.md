# sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/event/ConnectionClosed.java

Purpose: `ConnectionClosed` is an event carrying the closed server hostname and port.

Important APIs and control flow: constructor stores values; getters expose them; equality and hash code are value-based.

State, dependencies, and integration: published by `Connection.close` and consumed by `SMBClient` to remove cached connections and unregister servers.

Risks: hostname must be non-null for equality/hash code. Tests should verify event publication effects and value equality.
