## sources/distributed-fs/xrootd/src/XrdNet/XrdNetMsg.hh

Purpose: Declares a UDP message sender abstraction with default-destination and per-call-destination modes.

Important APIs and types: Three `Send` overloads support raw buffers, `XrdNetSockAddr`, and `iovec` payloads. Constructor accepts logger, optional destination, success flag, and refresh flag. Protected helpers manage readiness and error mapping.

Control flow: Header documents return semantics: negative for error, zero for sent, positive for timeout/not sent.

State and persistence: Holds non-owned logger, owned default destination string, socket fd, destination-valid flag, and refresh-registration flag. No persistence.

Dependencies and integration points: Includes socket headers and `XrdNetAddr.hh`; forward declares `XrdNetSockAddr` and `XrdSysError`. Used by notification and control-plane datagram senders.

Risks: Copy operations are not disabled, so copying would duplicate fd/string ownership. `FD` defaults to `-1`, but destructor behavior depends on implementation safeguards. `Send` uses `strlen` when length is zero, unsuitable for binary datagrams.

Test signals: Compile callers using all overloads; sanitizer tests for copy misuse, binary payloads with explicit length, and destructor after failed construction.
