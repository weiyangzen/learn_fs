# sources/distributed-fs/xrootd/src/XrdSecgsi/XrdSecgsiProxy.cc

## Purpose
`XrdSecgsiProxy.cc` implements the `xrdgsiproxy` command-line utility for creating, inspecting, validating, and deleting GSI proxy certificate files. It is not the server authentication protocol itself; it is an operator/user tool layered on top of the XRootD crypto factory APIs. It loads an X.509-capable crypto plugin, obtains function hooks for proxy creation and certificate parsing, and then drives a small mode-based CLI around proxy files.

## Important APIs, types, and functions
The file defines `kModes` values for `init`, `info`, `destroy`, and `help`, and it keeps the selected mode plus all CLI settings in process-global variables. Key globals include `CryptoMod`, `CAdir`, `CRLdir`, default certificate/key/proxy paths, `Valid`, `Bits`, `PathLength`, `ClockSkew`, and hook pointers such as `XrdCryptoX509ParseFile_t ParseFile`, `XrdCryptoX509CreateProxy_t CreateProxy`, `XrdCryptoX509GetVOMSAttr_t GetVOMSAttr`, and `XrdCryptoProxyCertInfo_t ProxyCertInfo`.

`main()` initializes tracing, loads `XrdCryptoFactory::GetCryptoFactory(CryptoMod)`, resolves required X.509 hooks, and dispatches by mode. `ParseArguments()` parses CLI options and validates filesystem prerequisites. `CheckOption()` recognizes exact option names and `no<name>` variants for boolean switches. `Display()` prints proxy certificate metadata, path-length constraints, key strength, remaining lifetime, VOMS attributes, and optional extension dumps.

## Control flow
Argument parsing is the first gate. Missing proxy path defaults to `/tmp/x509up_u<uid>`, and `init` defaults certificate and key paths to `$HOME/.globus/usercert.pem` and `$HOME/.globus/userkey.pem`. In `init`, the private key must be a regular file with owner-only read/write semantics. After parsing, `main()` sets trace masks, loads the crypto module, resolves the factory hooks, and then executes the selected mode.

`init` converts the requested validity string with `XrdSutParseTime()`, fills `XrdProxyOpt_t`, calls `X509CreateProxy`, and displays the first certificate in the resulting `XrdCryptogsiX509Chain`. `destroy` simply unlinks the proxy file. `info` parses the proxy file into a chain, requires at least two certificates unless `-exists` is being used, displays the proxy, and displays a parent proxy when the subject indicates a limited proxy. The `-exists` path is quiet and returns non-zero if the proxy is absent, too short-lived for `-valid`, or below the requested key strength.

## State and persistence behavior
Persistent state is limited to the proxy file named by `PXcert`; `init` writes it through the crypto factory, `destroy` removes it, and `info` reads it. The tool derives defaults from the current uid and home directory but does not maintain its own metadata. Runtime state is stored in globals, so the program is single-shot and not reentrant as a library.

## Dependencies and integration points
This utility integrates with `XrdCrypto` for X.509 parsing, proxy creation, extension decoding, VOMS extraction, and trace settings. It uses `XrdSut` helpers for time parsing and path expansion, `XrdSysPwd` for uid/home resolution, and `XrdSecgsiTrace.hh` for trace macros. It assumes the selected crypto plugin exports the specific X.509 hook table needed by the GSI implementation.

## Risks and edge cases
CLI parsing is manual and permissive: unknown options are ignored after printing, and some option validation relies on `errno` without visibly resetting it before `strtol()`. `-bits` clamps to at least 2048, which is conservative but may surprise callers asking to validate weaker legacy proxies. `-exists` only checks remaining lifetime and bit strength, not full chain trust. The default `CAdir` and `CRLdir` globals are parsed but not used in this file. Security-sensitive paths are expanded and checked, but proxy file permissions are not validated on read.

## Test signals
Useful tests include `xrdgsiproxy info -f <proxy>`, `xrdgsiproxy -exists -valid <duration> -bits <n> -f <proxy>` exit-code checks, `init` with a temporary certificate/key pair, `destroy` against a temporary proxy file, and negative tests for unreadable keys, bad permissions, malformed proxy chains, missing crypto hook functions, and `-extensions` dumping. Integration with `XrdSecgsitest.cc` covers the lower-level crypto/GSI operations that this tool calls.
