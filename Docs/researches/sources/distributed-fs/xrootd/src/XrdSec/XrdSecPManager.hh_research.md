# sources/distributed-fs/xrootd/src/XrdSec/XrdSecPManager.hh

Purpose: Declares the protocol manager used by both client and server security code to find, load, and instantiate authentication protocols.

Important APIs and types: Defines `XrdSecPMask_t`, the `PROTPARMS` function signature macro, and class `XrdSecPManager`. Public methods include `Find`, two `Get` overload groups, `Load`, `setDebug`, `setErrP`, and `protTLS`.

Control flow: Server startup loads configured protocols with `Load`; runtime server authentication calls `Get` by protocol name; clients call `Get` with server parameters to select a supported candidate.

State and persistence: Maintains a linked list of loaded protocols, next bitmask, logger pointer, TLS protocol string, and proxy/forwarded-credential policy flags. All state is in memory and effectively process-long.

Dependencies and integration points: Includes `XrdSecInterface.hh` and `XrdSysPthread.hh`; forward declares network, error, protocol, and logging classes. It is embedded statically in `XrdSecServer`.

Risks: Thread-safety depends on internal mutex use and the invariant that protocols are added but not removed. The API returns raw protocol pointers whose `Delete` method must be used. Proxy behavior changes client protocol selection by suppressing `xrd.wantprot`.

Test signals: Header consumers should compile in client and server contexts, exercise constructor proxy flags, and verify returned masks drive `protbind only` enforcement.
