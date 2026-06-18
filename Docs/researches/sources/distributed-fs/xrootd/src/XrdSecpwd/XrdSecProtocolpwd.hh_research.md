# sources/distributed-fs/xrootd/src/XrdSecpwd/XrdSecProtocolpwd.hh

## Purpose
`XrdSecProtocolpwd.hh` declares the password security protocol's public class, state containers, enums, constants, and helper method surface. It is the contract shared by the plugin implementation and build target for the password authentication module.

## Important APIs, types, and functions
The header defines protocol constants such as `XrdSecPROTOIDENT` (`"pwd"`), `XrdSecpwdVERSION`, buffer limits, option flags, and `XrdCryptoMax`. Its enums describe protocol status (`kpST_*`), auto-registration modes, autologin update modes, credential input sources, credential types, credential actions, client steps (`kXPC_*`), server steps (`kXPS_*`), and password-specific error codes.

`pwdStatus_t` is the compact status word exchanged in protocol buffers. `pwdOptions` aggregates client/server initialization settings parsed from environment or server parameters. `pwdHSVars` stores per-handshake mutable state: iteration, timestamp, crypto selection, user/tag, remote version, ciphers, cache entries, random-tag state, tty state, current/last step, system-password mode, AFS cell, and deferred parameters.

`XrdSecProtocolpwd` derives from `XrdSecProtocol` and declares `Authenticate()`, `getCredentials()`, constructor, `Delete()`, static `Init()`, `PrintTimeStat()`, and `EnableTracing()`. Private methods cover parsing, errors, credential querying/checking, timestamp/random-tag validation, saving/exporting, serialization, and hashing.

## Control flow
The header encodes the state-machine vocabulary used by the implementation. Client steps start with normal packets, server verification requests, signed random tags, credential packets, auto-registration, and failure acknowledgement. Server steps include initial parameters, credential requests, random-tag challenges, signed random-tag replies, new public keys, public keys after auto-registration, and failure. The implementation switches on these values in `getCredentials()` and `Authenticate()`.

## State and persistence behavior
The class declares extensive static state for persistent file names, PFile handles, caches, crypto factory slots, reference ciphers, runtime policy flags, and trace objects. Per-instance state includes endpoint address, options, client name, mode flag, handshake variables, and optionally retained client credentials. The header makes clear that persistence is mediated through `XrdSutPFile` and `XrdSutPFCache` rather than plain text structures.

## Dependencies and integration points
The header depends on XRootD network, error, threading, tokenizer, security interface, password tracing, SUT PFile/buffer/random helpers, and crypto factory/cipher APIs. Any source including it receives the protocol ABI and storage model needed by `XrdSecProtocolpwd.cc`.

## Risks and edge cases
Several constants enforce small legacy limits, including `kMAXUSRLEN` and `kMAXPWDLEN`, while implementation paths may handle longer values through dynamic strings and fixed arrays. `pwdStatus_t` is packed manually into an integer in the implementation, so field size and byte-order assumptions matter. The destructor for `pwdHSVars` deletes only selected pointers; other pointers are borrowed from static caches or factories and require disciplined ownership. The protocol class has many static mutable members, so initialization order and client/server mode separation are critical.

## Test signals
Compile coverage should ensure all enum values and method declarations match the implementation. Protocol tests should assert that status words, client step values, and server step values round-trip correctly through `XrdSutBuffer` serialization. Initialization tests should verify that `pwdOptions` defaults match expected server/client behavior and that `pwdHSVars` starts with safe empty state.
