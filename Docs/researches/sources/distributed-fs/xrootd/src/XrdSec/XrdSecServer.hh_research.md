# sources/distributed-fs/xrootd/src/XrdSec/XrdSecServer.hh

Purpose: Declares the default server-side security service implementation used by the `XrdSecgetService` plug-in entrypoint.

Important APIs and types: `XrdSecServer` privately inherits `XrdSecService` and implements `getParms`, `getProtocol`, `PostProcess`, `Configure`, and `protTLS`. Private helpers correspond to configuration directives and token/binding completion.

Control flow: Construction sets defaults and logger/trace state; `Configure` must succeed before the object is returned as an `XrdSecService`.

State and persistence: Holds static `PManager`, a union for pre-load versus loaded entity post-processing plugin state, binding list pointers, security token buffers, trace pointer, and policy flags. State is process-local and not deleted during normal server lifetime.

Dependencies and integration points: Includes `XrdSysError`, `XrdSysLogger`, `XrdOucStream`, `XrdSecInterface`, and `XrdSecPManager`; forward declares entity pinning and binding helpers.

Risks: Private inheritance still casts to `XrdSecService *` at the factory boundary. The union requires correct phase discipline between `pinInfo` and `secEntityPin`. The destructor is intentionally empty because the server is never deleted.

Test signals: Compile the factory cast, verify `protTLS` forwards manager state, and run lifecycle tests that call `Configure` once then service methods concurrently.
