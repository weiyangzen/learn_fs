<!-- BEGIN_FILE_RESEARCH: sources/test-tools/pynfs/nfs4.0/lib/rpc/rpc.py -->
# sources/test-tools/pynfs/nfs4.0/lib/rpc/rpc.py

Purpose: core ONC RPC transport layer for pynfs. It implements record-marked TCP RPC clients, a poll-based RPC server, RPC reply validation, XID tracking, reconnection/resend behavior, and pluggable security flavors.

Important APIs/types/functions: socket monkey patches `_recv_all()`, `_recv_record()`, and `_send_record()` implement RFC record marking. `RPCClient` owns per-thread sockets, packers/unpackers, outstanding XID caches, `send()`, `listen()`, `call()`, `get_call_header()`, and `check_reply()`. `Server` abstracts poll/select event dispatch. `RPCServer` accepts connections, buffers record fragments, dispatches command records, decodes RPC calls, invokes `handle_<proc>()`, applies security unwrapping/wrapping, and packs accepted/denied replies. Exceptions `RPCError`, `RPCAcceptError`, and `RPCDeniedError` expose protocol errors.

Control flow/state: clients create one TCP socket per thread, assign monotonically wrapping XIDs, cache request headers/data until a matching reply arrives, and cache out-of-order replies. Servers keep dictionaries keyed by fd for read buffers, write buffers, partial packets, queued records, and sockets. Security objects mediate credentials, verifiers, and data wrapping.

Dependencies/integration: depends on generated `rpc_const`, `rpc_type`, `rpc_pack`, optional GSS security, Python sockets, poll/select, and threading. `nfs4lib.NFS4Client` subclasses `RPCClient`; callback server subclasses `RPCServer`.

Risks/test signals: monkey-patching `socket.socket` is global. Reconnect resends can duplicate non-idempotent calls if the server processed a request before disconnect. Some `raise` statements lack explicit exception objects. Test signals include RPC mismatch/auth exceptions, duplicate XID errors, truncated record handling, and server fd cleanup on poll errors.
<!-- END_FILE_RESEARCH: sources/test-tools/pynfs/nfs4.0/lib/rpc/rpc.py -->
