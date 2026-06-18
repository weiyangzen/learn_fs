<!-- BEGIN_FILE_RESEARCH: sources/test-tools/pynfs/nfs4.0/nfs4lib.py -->
# sources/test-tools/pynfs/nfs4.0/nfs4lib.py

Purpose: high-level NFSv4 client library for pynfs. It wraps the lower RPC layer with NFSv4 COMPOUND construction/validation, generated XDR packers/unpackers, callback server handling, file/object helpers, stateid/seqid management, ACL/attribute conversion helpers, and URL parsing.

Important APIs/types/functions: exception classes `BadCompoundRes`, `UnexpectedCompoundRes`, and `InvalidCompoundRes` represent NFS protocol failures. `FancyNFS4Packer/Unpacker` convert bitmaps, fattrs, and dirlists into friendlier Python forms. `CBServer` handles callback NULL and CB_COMPOUND with CB_GETATTR and CB_RECALL support. `NFS4Client` extends `rpc.RPCClient` and provides `compound()`, `init_connection()`, `setclientid()`, `open()`, path helpers, getattr/readdir/read/write/create/remove/rename/open-confirm/lock/close/commit helpers, and tree creation. Module functions include `check_result()`, attribute bit-name caches, `dict2fattr()`, `fattr2dict()`, `list2bitmap()`, `bitmap2list()`, and `parse_nfs_url()`.

Control flow/state: client construction starts a callback RPC server thread, opens a callback control socket, initializes RPC security, and tracks `clientid`, callback ids, owner sequence ids, verifier, homedir, and options. `compound()` packs operations, retries `NFS4ERR_DELAY`, unpacks results, and enforces response operation ordering/status invariants. File/open/lock helpers update seqids only when protocol rules allow. Callback recall state is protected by a lock and reset after recall handling.

Dependencies/integration: depends on `rpc.rpc`, generated NFSv4 constants/types/packers, `nfs_ops.NFS4ops`, sockets, threading, inspect, and Python XDR error classes. It is the central integration layer for pynfs automated tests and the interactive client.

Risks/test signals: several code comments mark stubs/FIXMEs around callbacks, retry behavior, and server quirks. Mutable default arguments are used for attrs/sec lists/path defaults. A visible duplicate line in `do_readdir()` suggests source hygiene risk. Test signals are raised NFS exceptions, invalid compound validation failures, callback op counts/results, and helper-returned status fields such as read data, write count, lockid, and stateid.
<!-- END_FILE_RESEARCH: sources/test-tools/pynfs/nfs4.0/nfs4lib.py -->
