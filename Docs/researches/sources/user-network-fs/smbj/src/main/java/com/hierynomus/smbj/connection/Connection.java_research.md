# sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/connection/Connection.java

Purpose: `Connection` is the live transport/session coordinator for one SMB server connection.

Important APIs and control flow: construction creates the transport and packet handler chain. `connect` opens the socket, creates `ConnectionContext`, negotiates dialect, initializes encryption, and selects local or DFS path resolving. `authenticate` delegates session establishment to `SMBSessionBuilder`. `send` assigns credits and message IDs under a lock, registers an outstanding request, writes the packet, and returns a cancellable future. Incoming packets are passed through the handler chain.

State, dependencies, and integration: it owns `SessionTable`, preauth session table, `OutstandingRequests`, `SequenceWindow`, signatory, encryptor, transport, event bus, server list, and path resolver. It extends `Pooled` for client connection reuse.

Risks: send ordering and credit accounting are concurrency-sensitive. Cancel assumes the session is still present. Forced close skips session logoff. Test signals include negotiation, request registration/removal, credit assignment, cancellation, error propagation to outstanding requests, close events, packet handler ordering, and DFS resolver selection.
