<!-- BEGIN_FILE_RESEARCH: sources/test-tools/pynfs/nfs4.0/nfs4client.py -->
# sources/test-tools/pynfs/nfs4.0/nfs4client.py

Purpose: interactive Python shell for manually driving an NFSv4 server with pynfs operations.

Important APIs/types/functions: `PyShell` subclasses `code.InteractiveConsole`, creates `nfs4lib.NFS4Client("myid", server, homedir=[])`, imports generated NFSv4 types/constants into locals, exposes client operation builders as uppercase commands, and binds readline tab completion. `modify_packers()` improves `entry4.__repr__`. `main()` launches the shell with a prompt hint.

Control flow/state: startup adjusts `sys.path` when run from package root, initializes a live NFS4 client and callback server through `nfs4lib`, then enters an interactive console. Completion evaluates dotted expressions against shell locals.

Dependencies/integration: depends on readline, generated `xdrdef` modules, `nfs4lib`, and an accessible NFS server argument. It is a developer/test operator tool rather than automated test code.

Risks/test signals: completion uses `eval()` on partially typed expressions, acceptable for an interactive trusted shell but unsafe for untrusted input. Runtime signals are interactive RPC responses, exceptions, and printed tracebacks.
<!-- END_FILE_RESEARCH: sources/test-tools/pynfs/nfs4.0/nfs4client.py -->
