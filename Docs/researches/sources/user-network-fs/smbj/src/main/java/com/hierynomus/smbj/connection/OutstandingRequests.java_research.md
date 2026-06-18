# sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/connection/OutstandingRequests.java

Purpose: `OutstandingRequests` tracks sent requests awaiting responses and cancellation lookup.

Important APIs and control flow: read lock methods check and retrieve by message ID or cancel ID. `registerOutstanding` inserts into both maps. `receivedResponseFor` removes from both maps and throws if missing. `handleError` drains all requests and delivers the error to their promises.

State, dependencies, and integration: protected by `ReentrantReadWriteLock`; used by `Connection.send` and packet handlers.

Risks: duplicate message IDs overwrite prior requests. Missing responses become runtime exceptions. Tests should cover concurrent registration/response, cancellation lookup, duplicate handling expectations, and error fan-out.
