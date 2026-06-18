# sources/test-tools/crashmonkey/code/utils/communication/BaseSocket.cpp

Purpose: implements low-level serialization for CrashMonkey control messages over sockets. It reads and writes command-only `SocketMessage` instances using network byte order.

Important APIs/types/functions: `ReadMessageFromSocket`, `WriteMessageToSocket`, `GobbleData`, `ReadIntFromSocket`, `WriteIntToSocket`, `ReadStringFromSocket`, `WriteStringToSocket`, `recv`, `send`, `htonl`, and `ntohl`. Current message handling accepts only command types with no payload.

Control flow: reads type and size, switches over known commands, gobbles unexpected payload bytes, and returns -1 for unknown types. Writing sends type, validates it is a known command, writes size 0, and returns status.

State/persistence behavior: no persistent state; the functions consume or emit bytes on a connected socket. Dependencies/integration: used by `ClientSocket` and `ServerSocket`.

Risks/test signals: zero-length `recv` is not handled as disconnect and can spin, variable-length stack arrays are used, string helpers are unused by current command path, and error reporting is coarse. Socket tests are not present in this subset.
