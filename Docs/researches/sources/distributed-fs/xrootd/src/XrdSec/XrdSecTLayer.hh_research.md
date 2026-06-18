# sources/distributed-fs/xrootd/src/XrdSec/XrdSecTLayer.hh

Purpose: Declares `XrdSecTLayer`, an abstract `XrdSecProtocol` wrapper that virtualizes a transport socket for protocols that require stream-socket handshakes.

Important APIs and types: `Initiator` selects client- or server-first flow. Derived classes implement `secClient`, `secServer`, and `Delete`. The class overrides `Authenticate` and `getCredentials`, exposes `secXeq`, and defines internal `TLayerRR` frame constants.

Control flow: Client and server call the normal security protocol methods, while derived implementations communicate on a supplied file descriptor in a helper thread.

State and persistence: Stores thread, semaphore, socket descriptors, timeout counters, error state, and frame header. State is transient per authentication object.

Dependencies and integration points: Includes `XrdSecInterface` and `XrdSysPthread`; forward declares `XrdOucErrInfo`. It is intended as a base for SSL/TLS-like protocols integrated into XRootD auth handshakes.

Risks: Documentation requires derived `Delete` to join the thread, but the base cannot enforce it. Protocols must tolerate a local 127.0.0.1-style virtual socket identity. `Tmax` is fixed internally.

Test signals: Compile a mock derived class, verify both initiator modes, ensure destructor closes `myFD`, and check derived `Delete` joins active threads.
