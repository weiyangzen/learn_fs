# sources/distributed-fs/xrootd/src/XrdSec/XrdSectestClient.cc

Purpose: Legacy command-line utility that converts a security token into client credentials for manual or scripted protocol testing.

Important APIs and functions: `main` parses `-b`, `-d`, `-l`, and `-h`, obtains `XrdSecGetProtocol`, calls `getCredentials`, and prints binary or hex output. `tohex` converts bytes to lowercase hex. `help` prints usage.

Control flow: The tool reads the sectoken from argv or `XrdSecSECTOKEN`, resolves the target host or defaults to localhost, optionally sets `XrdSecDEBUG`, gets a protocol object, generates credentials, optionally prefixes length, writes credentials, and calls `Delete`.

State and persistence: No persistent state. It uses environment variables for input and debug behavior and writes credentials to stdout.

Dependencies and integration points: Links to the client-side `XrdSecGetProtocol` symbol, `XrdNetAddr`, and security interface types. It pairs with `XrdSectestServer.cc`.

Risks: The source references `eText` and `pp->addrInfo` in ways that appear stale relative to the shown interfaces, so build coverage is important. Binary `fwrite` checks compare item count against byte size, which is incorrect for a one-item write. Credentials are printed to stdout and may expose secrets.

Test signals: Build the utility, run host and real protocol tokens, binary and hex output, length prefix, invalid host, missing token, debug mode, and pipe output into the test server.
