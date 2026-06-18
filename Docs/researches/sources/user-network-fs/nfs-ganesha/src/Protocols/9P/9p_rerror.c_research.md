## sources/user-network-fs/nfs-ganesha/src/Protocols/9P/9p_rerror.c

Purpose: common 9P error response encoder.

APIs and flow: `_9p_rerror` builds `RERROR`, writes the request tag and errno value, finalizes/checks reply length, maps the original request opcode to a function name for logging, and returns success to the transport layer so the error reply is sent.

State/dependencies: no persistent state beyond reply buffer mutation. It depends on `_9pfuncdesc` for log names and 9P wire macros.

Risks/tests: if `msgtag` is invalid or unavailable, error replies can carry the wrong tag. Test all handlers' error paths, unsupported opcodes, bounds behavior, and errno/log message mapping.
