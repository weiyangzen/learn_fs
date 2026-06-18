# sources/distributed-fs/xrootd/src/XrdSec/XrdSectestServer.cc

Purpose: Legacy command-line utility that feeds credentials into the server security service and prints the authenticated entity.

Important APIs and functions: `main` creates `XrdSecgetService`, prints the service token, reads credentials in binary or hex, calls `getProtocol` and `Authenticate`, and prints `name@host prot=...`. Helpers parse arguments, read binary credentials, convert hex with `unhex`/`cvtx`, read lines, and print errors/help.

Control flow: Command-line options set config path, host, input source, binary mode, and debug flag. The server service is configured from `-c`, host defaults to localhost, credentials come from inline argument, file/stdin, or binary stream, then normal server authentication APIs are exercised.

State and persistence: Uses global `opts`, `errbuff`, and `hexbuff`. No durable writes; output goes to stdout/stderr.

Dependencies and integration points: Links directly to `XrdSecgetService`, `XrdSysLogger`, `XrdOucErrInfo`, `XrdNetAddr`, and XrdSec interfaces. Intended for manual interoperability with test client and real protocol plug-ins.

Risks: Several parsed options in the usage string are legacy or unimplemented. `opts.xtra` and `opts.debug` are parsed but not materially used. Credential buffer size is fixed at 8192 bytes for binary input and 4096 bytes for hex conversion in `main`. The call to `getParms` passes `opts.host` where the interface expects `XrdNetAddrInfo *`, suggesting this file may be excluded or stale in current builds.

Test signals: Build test target, run with valid/invalid config, inline hex credentials, stdin/file input, binary input, malformed hex, oversized credentials, missing config, host auth, and multi-step protocols returning continuation parameters.
