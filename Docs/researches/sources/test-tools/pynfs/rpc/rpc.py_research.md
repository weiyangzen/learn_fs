# sources/test-tools/pynfs/rpc/rpc.py

Purpose: TCP ONC RPC transport implementation with record marking, asynchronous polling, per-call deferred replies, client/server base classes, and hooks into RPC authentication/security.

Important APIs/types/functions: `inc_u32`, exceptions `RPCError/RPCTimeout/RPCAcceptError/RPCDeniedError`, `FancyRPCUnpacker`, `FancyRPCPacker`, `DeferredData`, `Alarm`, `Pipe`, `RpcPipe`, `ConnectionHandler`, `Server`, and `Client`.

Control flow: `ConnectionHandler.start` runs a `select` loop over listening sockets, active pipes, write-ready pipes, and an internal alarm connection. Incoming bytes are reassembled by `Pipe.recv_records` using RFC record marks, then each full RPC record is dispatched to a worker thread. Calls are unpacked, RPC version/auth/program/version/procedure are checked, procedure handlers run, results are secured and sent as replies. Client calls allocate an XID, pack a CALL, store `DeferredData`, send the record, and wait for the matching reply.

State and persistence behavior: runtime state includes socket sets, fd-to-pipe maps, write/read buffers, pending XID map, XID counter, security flavor instances, and active flags. There is no durable persistence.

Dependencies/integration: depends on generated RPC XDR pack/type/const modules, `security`, `rpclib`, Python `socket/select/threading`, and subclass implementations of program/version/procedure lookup.

Risks and test signals: heavily threaded with daemon workers and a custom alarm socket. Some exception paths drop requests silently. `RpcPipe.rcv_reply` catches `IndexError` for missing XID even though dict lookup raises `KeyError`. `expose(safe=True)` buzzes a string command instead of bytes in one branch, which can matter on Python 3 if used.
