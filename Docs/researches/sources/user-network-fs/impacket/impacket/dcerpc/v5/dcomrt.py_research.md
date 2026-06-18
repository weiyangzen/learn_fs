# sources/user-network-fs/impacket/impacket/dcerpc/v5/dcomrt.py

## Purpose
`dcomrt.py` implements Impacket's core `[MS-DCOM]` runtime support. It defines DCOM wire structures, OBJREF formats, activation property blobs, object exporter calls, remote activation calls, `IRemUnknown` reference-management calls, and connection helpers that activate remote COM classes and keep remote OIDs alive.

## Important APIs, Types, and Functions
- DCOM identifiers include CLSIDs for activation property records and IIDs for `IActivation`, `IRemoteSCMActivator`, `IObjectExporter`, `IRemUnknown`, `IRemUnknown2`, `IUnknown`, and `IClassFactory`.
- Wire structures include `COMVERSION`, `ORPCTHIS`, `ORPCTHAT`, `MInterfacePointer`, `OBJREF`, `STDOBJREF`, `OBJREF_STANDARD`, `OBJREF_HANDLER`, `OBJREF_CUSTOM`, `OBJREF_EXTENDED`, `DUALSTRINGARRAY`, `STRINGBINDING`, `SECURITYBINDING`, `Context`, `ORPC_CONTEXT`, and activation blob structures such as `CustomHeader`, `ACTIVATION_BLOB`, `InstantiationInfoData`, `ActivationContextInfoData`, `ScmRequestInfoData`, `ScmReplyInfoData`, and `PropsOutInfo`.
- RPC call classes include `ResolveOxid`, `SimplePing`, `ComplexPing`, `ServerAlive`, `ResolveOxid2`, `ServerAlive2`, `RemoteActivation`, `RemoteGetClassObject`, `RemoteCreateInstance`, `RemQueryInterface`, `RemAddRef`, and `RemRelease`.
- `DCOMConnection` owns target credentials, the portmap DCE/RPC connection, OID ping sets, a class-level ping timer, `CoCreateInstanceEx()`, `get_dce_rpc()`, and `disconnect()`.
- `CLASS_INSTANCE` stores ORPC headers, resolved string bindings, and negotiated auth type/level for an activated class.
- `INTERFACE` wraps target, IPID, OID, OXID, object references, and per-thread DCE bindings; it parses object references, connects to object endpoints, sends DCOM requests, and disconnects object endpoint transports.
- `IRemUnknown` and `IRemUnknown2` expose `RemQueryInterface`, `RemAddRef`, and `RemRelease`.
- `IObjectExporter`, `IActivation`, and `IRemoteSCMActivator` expose activation, OXID resolution, alive checks, pinging, and class-object/instance activation.

## Control Flow
A `DCOMConnection` is initialized with target and credentials, creates an `ncacn_ip_tcp` transport, applies NTLM or Kerberos settings, sets the requested RPC authentication level, connects to the endpoint mapper/portmap, and stores the DCE connection in class-level `PORTMAPS`. `CoCreateInstanceEx()` uses `IRemoteSCMActivator.RemoteCreateInstance()` to activate a requested CLSID/IID and starts the keepalive ping timer when OXID resolver support is enabled.

Activation calls build ORPC headers and activation-property blobs, request TCP protocol sequence 7, send `RemoteCreateInstance` or `RemoteGetClassObject`, parse the returned custom OBJREF activation blob, extract `ScmReplyInfoData` for OXID bindings and `PropsOutInfo` for interface data, create a `CLASS_INSTANCE`, set auth hints from the server reply, and return an `IRemUnknown2` wrapping the requested interface pointer.

`INTERFACE.process_interface()` parses `OBJREF_*` bytes and, for standard/handler/extended references, records IPID, OID, and OXID. Unless `SORF_NOPING` is set, the OID is added to `DCOMConnection.OID_ADD`. `INTERFACE.connect()` reuses or creates one DCE object-endpoint connection per target/thread/OXID. It selects a TCP string binding from the activation reply, handles FQDN matching and NetBIOS substitution, copies credentials and Kerberos settings from the portmap transport, applies auth level/type from the class instance, connects, binds or alter-contexts to the requested IID, and stores the active binding.

`INTERFACE.request()` injects the stored ORPC header into each `DCOMCALL`, connects or adjusts context for the IID, sends the request using the object endpoint DCE connection, and transforms `RPC_E_DISCONNECTED` failures into a clearer keepalive warning. The ping timer periodically calls `DCOMConnection.pingServer()`, which sends `ComplexPing` when OIDs have been added or deleted and `SimplePing` otherwise.

## State and Persistence Behavior
All state is in process memory:
- `DCOMConnection.PORTMAPS` maps target names to shared portmap DCE objects.
- `DCOMConnection.OID_ADD`, `OID_DEL`, and `OID_SET` track OID lifetime and ping set IDs by target.
- `DCOMConnection.PINGTIMER` is a class-level `threading.Timer` that reschedules itself every 120 seconds.
- `INTERFACE.CONNECTIONS` maps target, thread name, and OXID to object endpoint DCE connections and current IID binding.
- `CLASS_INSTANCE` retains the ORPC header, server string bindings, auth type, and auth level.
No durable persistence is performed. Remote COM object lifetimes are affected by OID pinging and `RemRelease`; `disconnect()` removes local connection/ping state and cancels the timer when no portmaps remain.

## Dependencies and Integration Points
This file depends on Impacket NDR, DCE/RPC transport, type serialization, HRESULT metadata, UUID utilities, socket address parsing, `threading.Timer`, and RPC authentication constants. It is the foundation for higher-level DCOM modules such as `dcom/wmi.py`, which inherit `IRemUnknown` and `INTERFACE` behavior. Integration points include the endpoint mapper, the remote SCM activator, the object exporter, per-object endpoint bindings returned in dual-string arrays, and Kerberos/NTLM credential propagation from the portmap transport to object transports.

## Risks and Edge Cases
- Class-level dictionaries and ping sets are not protected by locks; concurrent activations, releases, and ping timer runs can race.
- `pingServer()` iterates and mutates class-level dictionaries and catches broad exceptions, so failures can hide stale OID state.
- `ComplexPing()` accepts a `sequenceNum` argument but writes `SequenceNum` from `setId`, likely ignoring the supplied sequence number.
- `OBJREF_EXTENDED.__init__()` sets `Signature1` twice and sets `nElms` to the signature value, which looks suspicious and needs protocol validation.
- `INTERFACE.connect()` only accepts TCP tower id 7 and may fail with endpoints that prefer other protocol sequences.
- Target matching for string bindings is heuristic and can fail with unusual DNS suffixes, IPv6 formatting, NetBIOS names, or NAT/forwarded bindings.
- `INTERFACE.CONNECTIONS[self.__target][current_thread().name] = {}` replaces existing per-thread OXID entries when creating a new object connection, which can discard other OXID connections for the same thread.
- Activation helpers mostly support one IID at a time despite protocol fields allowing multiple requested interfaces.
- Some response HRESULT/error fields are not explicitly checked before wrapping returned interface data.
- The runtime assumes NDR32 layouts and Impacket type serialization behavior matching the target DCOM implementation.

## Test Signals
Useful tests should include:
- Golden NDR encode/decode tests for `OBJREF_*`, `DUALSTRINGARRAY`, `ACTIVATION_BLOB`, `ScmReplyInfoData`, and `PropsOutInfo`.
- Mock DCE tests for `RemoteCreateInstance`, `RemoteGetClassObject`, `ResolveOxid`, `ServerAlive2`, `RemQueryInterface`, `RemAddRef`, and `RemRelease` request fields and response wrapping.
- Unit tests for `COMVERSION.set_default_version()`, `CLASS_INSTANCE.get_auth_level()`, `handle_t.isNull()`, and object-reference parsing with and without `SORF_NOPING`.
- Connection-selection tests covering IPv4, IPv6, FQDN, NetBIOS-derived bindings, Kerberos remote host/name propagation, alter-context reuse, and multiple OXIDs in one thread.
- Timer/lifetime tests that simulate OID add/delete sets and verify `ComplexPing`, `SimplePing`, `RemRelease`, and `disconnect()` state cleanup.
- Integration tests against a Windows host for remote activation of a known class, query-interface, method call through a higher-level module, idle keepalive, and clean release/disconnect.
