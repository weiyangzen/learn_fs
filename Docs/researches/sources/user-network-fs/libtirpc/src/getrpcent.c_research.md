## sources/user-network-fs/libtirpc/src/getrpcent.c

Purpose: Supplies fallback implementations for RPC database functions when libc lacks them: `getrpcbynumber`, `getrpcbyname`, `setrpcent`, `endrpcent`, and `getrpcent`.

Important APIs and control flow: A process-global `rpcdata` structure holds the `/etc/rpc` file, stay-open flag, aliases, current line, and optional YP state. Lookup by number/name rewinds with `setrpcent`, iterates `getrpcent`, and closes with `endrpcent`. `getrpcent` reads a line or YP record and passes it to `interpret`, which strips comments/newlines, parses service name, numeric program, and aliases into static storage.

State and persistence: Global static `rpcdata` is reused and not thread-specific. File handle persistence is controlled by `stayopen`.

Dependencies and integration: Supports `getrpcport` and applications needing RPC program database lookup.

Risks and test signals: Non-thread-safe static result storage and recursive skip of malformed/comment lines are important. Tests should cover comments, aliases, malformed lines, stayopen behavior, YP fallback guards, and repeated calls overwriting previous results.
