# sources/user-network-fs/impacket/tests/dcerpc/test_dcomrt.py

Purpose: exercises Impacket DCOM runtime bindings, activation, object exporter, remote SCM activation, interface querying, and COM Event System helper wrappers.

Important APIs and functions: `DCOMTests` uses TCP DCOM with NTLM packet integrity. It covers `IObjectExporter.ServerAlive`, `ServerAlive2`, `ComplexPing`, `SimplePing`, `ResolveOxid`, `ResolveOxid2`, `IActivation.RemoteActivation`, `IRemoteSCMActivator.RemoteCreateInstance`, and `RemoteGetClassObject`. `DCOMConnectionTests` exercises `DCOMConnection.CoCreateInstanceEx`, `RemQueryInterface`, `RemRelease`, `comev.IEventSystem`, `oaut.IDispatch`, type-info enumeration, and Event System collection enumeration.

Control flow: most tests bind to DCOM TCP, instantiate Event System COM objects, and call one runtime method. `RemoteGetClassObject` uses a `DCOMConnection` directly and releases the interface in `finally`. The `test_comev` path walks type information and enumerates Event Subscription/Event Class collections, releasing interfaces.

State and persistence behavior: tests are mostly read-only COM activation/enumeration. Skipped exploratory tests for VSS, VDS, OAUT, and IE show broader potential but do not run.

Dependencies and integration points: uses `tests.RemoteTestCase`, `tests.dcerpc.DCERPCTests`, `impacket.dcerpc.v5.dcomrt`, and COM helper modules `scmp`, `vds`, `oaut`, and `comev`. Requires remote DCOM firewall/configuration and privileges for COM activation.

Risks: file defines two classes named `DCOMTestsTCPTransport`; the second NDR64 class overwrites the first name in module scope, likely losing the NDR transport class from unittest discovery. Some tests do not always release activated COM interfaces. Event System contents vary by host. DCOM hardening and firewall policy can make failures environmental.

Test signals: validates DCOM endpoint binding, OXID resolution, activation, class factory retrieval, remote unknown lifetime operations, and high-level Event System wrappers.
