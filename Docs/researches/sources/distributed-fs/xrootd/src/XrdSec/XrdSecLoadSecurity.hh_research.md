# sources/distributed-fs/xrootd/src/XrdSec/XrdSecLoadSecurity.hh

Purpose: Declares ABI-stable loader utilities for client security factories, server security services, and client request-protection objects.

Important APIs and types: Exposes `XrdSecLoadSecFactory`, `XrdSecGetProtection`, and `XrdSecLoadSecService`. Forward declares `XrdSecProtect`, `XrdSecProtector`, `ServerResponseBody_Protocol`, and `XrdSysError`.

Control flow: Callers use `XrdSecLoadSecFactory` client-side to obtain `XrdSecGetProtocol`, use `XrdSecLoadSecService` server-side to instantiate `XrdSecService`, and use `XrdSecGetProtection` after authentication when the server's protocol response requests signed requests.

State and persistence: The header declares no state. Implementations cache loaded plug-ins process-wide and return long-lived service/protector pointers.

Dependencies and integration points: Includes `XrdSecInterface.hh` for protocol and service ABI types and references protocol response structures from `XProtocol`.

Risks: Comments document ABI stability, so signature or ownership changes are high impact. Error handling is split: factory loading returns text in a caller buffer, while service loading logs through `XrdSysError`.

Test signals: Compile client and server users against the header, verify default arguments, and check that callers interpret positive, zero, and negative `XrdSecGetProtection` results correctly.
