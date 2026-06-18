# sources/distributed-fs/xrootd/src/XrdSec/XrdSecProtocolhost.hh

Purpose: Declares the builtin host-based `XrdSecProtocol` implementation and factory.

Important APIs and types: `XrdSecProtocolhost` overrides `Authenticate`, `getCredentials`, and `Delete`, and provides `getParms` returning `"host"`. Private state stores `XrdNetAddrInfo epAddr` and `char *theHost`.

Control flow: Constructed with a host string and endpoint, then used like any other protocol through the base `XrdSecProtocol` methods.

State and persistence: Owns duplicated host memory and endpoint copy until `Delete`. No durable state and no cryptographic key state.

Dependencies and integration points: Includes `XrdNetAddrInfo` and `XrdSecInterface`. The non-extern factory `XrdSecProtocolhostObject` is referenced directly by `XrdSecPManager`.

Risks: Header-level `getParms` returns size 5 for a four-character string plus terminator, while other token sizes typically exclude terminators. Authentication strength is host-trust only.

Test signals: Verify constructor/destructor ownership, returned parameter size expectations, and factory compatibility with `PROTPARMS`.
