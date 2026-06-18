## sources/user-network-fs/nfs-ganesha/src/Protocols/9P/9p_version.c

Purpose: negotiates 9P protocol version and message size.

APIs and flow: `_9p_version` parses tag, requested msize, and version string; accepts strings matching `9P2000.L`; clamps requested msize to the connection maximum or lowers connection msize; rejects values under 512; and returns `RVERSION` with the accepted values.

State/dependencies: mutates `req9p->pconn->msize`, which later handlers use for reply and I/O bounds. Depends on string comparison and wire helpers.

Risks/tests: test exact and longer/shorter version strings, too-small msize, client-requested shrink, server-side cap, and all later handlers respecting negotiated msize.
