## sources/distributed-fs/xrootd/src/XrdNet/XrdNet.hh

Purpose: Declares the high-level XrdNet networking façade for TCP, UDP, and Unix-domain accept/connect operations.

Important APIs and types: Public methods include two `Accept` overloads, two `Bind` overloads, two `Connect` overloads, `Port`, `Relay`, `Secure`, `setDefaults`, `setDomain`, `Trim`, `unBind`, and `WSize`. Protected members expose fd, port, domain, defaults, security, and UDP buffer queue to derived classes.

Control flow: The header documents option semantics for accept, bind, and connect operations and defines the private helper split between TCP and UDP accepts.

State and persistence: The class owns an active socket fd and UDP buffer queue for its lifetime and frees the domain string in the destructor. It does not persist configuration outside process memory.

Dependencies and integration points: Includes platform socket headers and `XrdNetOpts.hh`; forward declares `XrdNetAddr`, `XrdNetPeer`, `XrdNetSecurity`, `XrdNetBufferQ`, and `XrdSysError`. This header is included by server code and message helpers that need network setup.

Risks: The interface returns `int` booleans for many operations and negative errno for bind failures, so callers must interpret results per method. `Secure` documentation transfers ownership but the type is a raw pointer. `setDefaults` applies options that cannot be disabled on individual calls.

Test signals: Compile consumers using both modern and legacy APIs; verify documented option bits match `XrdNetSocket` behavior; run leak/fd-close tests around constructor/destructor and repeated `Bind`/`unBind`.
