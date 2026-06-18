# sources/distributed-fs/xrootd/src/XrdSec/XrdSecProtocolhost.cc

Purpose: Implements the builtin `host` authentication protocol, a minimal protocol that identifies the peer by host/address rather than cryptographic credentials.

Important APIs and functions: `Authenticate` fills `Entity.prot`, `Entity.host`, and `Entity.addrInfo` and succeeds. `getCredentials` returns a credential buffer containing `host`. `XrdSecProtocolhostObject` constructs `XrdSecProtocolhost`.

Control flow: The protocol manager special-cases `host` and binds this factory directly. On client credential generation it sends the protocol name. On server authentication it accepts and populates entity host/address.

State and persistence: Each object owns a duplicated host string and a copied `XrdNetAddrInfo`. No persistent state or session key exists.

Dependencies and integration points: Depends on `XrdSecProtocolhost.hh` and `XrdSecInterface`. It is loaded through `XrdSecPManager` without a dynamic initializer.

Risks: Provides no cryptographic authentication and can negate other default protocols when enabled. `getCredentials` returns a string literal through `XrdSecCredentials`, relying on constructor ownership behavior to avoid freeing it. `Authenticate` ignores credential contents.

Test signals: Enable implicit host auth, generate credentials, authenticate null/host credentials through server code, verify entity fields, and ensure request protection is not enabled without a session key unless forced.
