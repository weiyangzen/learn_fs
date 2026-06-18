# sources/test-tools/crashmonkey/code/utils/communication/BaseSocket.h

Purpose: declares shared socket message encoding helpers for CrashMonkey client and server sockets. It centralizes command message read/write behavior.

Important APIs/types/functions: class `BaseSocket`, public static `ReadMessageFromSocket` and `WriteMessageToSocket`, private helpers for ints, strings, and payload discard, plus `SocketMessage` from `SocketUtils.h`.

Control flow: the header exposes only static utility entry points; implementations perform blocking socket reads/writes and command validation. State/persistence behavior: stateless utility with no owned resources.

Dependencies/integration: included by `ClientSocket.h` and `ServerSocket.h`. Risks/test signals: private string helpers are declared despite the current protocol using no string payloads, which can hide untested code paths if payload-bearing commands are later added.
