# sources/distributed-fs/xrootd/src/XrdSecsss/XrdSecProtocolsss.hh

Purpose: class declaration for the SSS security protocol object implementing `XrdSecProtocol`.

Important APIs and types: declares `Authenticate()`, `getCredentials()`, `Delete()`, `Init_Client()`, `Init_Server()`, static `Load_Client()`, `Load_Server()`, `eMsg()`, `Fatal()`, and nested `Crypto` descriptor. Private methods cover encoding/decoding, credential selection, crypto loading, endpoint setup, and identity string packing.

Control flow: the constructor records protocol name `sss`, duplicates the remote host name, and stores endpoint IP formats. Object creation through the plugin ABI calls init methods, while deletion is explicit through `Delete()` because the destructor is private.

State and persistence: declares static defaults shared across instances: keytab object, crypto object, ID map, allowed proxy protocols, static identity, lifetime, and mode flags. Instance state tracks active keytab/crypto, endpoint, serialized identity buffer, data options, sequence state, and V2 endpoint negotiation.

Dependencies and integration: includes crypto-lite, network endpoint, security interface, keytab, ID, and record/response headers. This header is the integration contract between the plugin ABI and SSS implementation internals.

Risks: static mutable fields mean process-global behavior can be surprising in tests or mixed client/server contexts. The private destructor requires all users to call `Delete()`. `char *` ownership is manual.

Test signals: compile ABI exports against this declaration, instantiate client/server objects, call `Delete()` under leak sanitizers, and verify static defaults are initialized exactly once.
