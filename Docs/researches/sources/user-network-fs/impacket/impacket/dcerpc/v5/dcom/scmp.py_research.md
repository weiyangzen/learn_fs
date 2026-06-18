# sources/user-network-fs/impacket/impacket/dcerpc/v5/dcom/scmp.py

## Purpose

`scmp.py` implements DCOM stubs for the Shadow Copy Management Protocol Interface (MS-SCMP). It exposes VSS/SCMP CLSIDs and IIDs, NDR structures for VSS management objects, call classes for querying snapshot providers, volumes, snapshots, and diff areas, and wrapper classes around the corresponding remote interfaces.

## Important APIs, Types, and Functions

Constants include `CLSID_ShadowCopyProvider`, `IID_IVssSnapshotMgmt`, `IID_IVssEnumObject`, `IID_IVssDifferentialSoftwareSnapshotMgmt`, `IID_IVssEnumMgmtObject`, and `IID_ShadowCopyProvider`. Types include `VSS_ID`, `VSS_PWSZ`, `VSS_TIMESTAMP`, `VSS_OBJECT_TYPE`, `VSS_MGMT_OBJECT_TYPE`, `VSS_VOLUME_SNAPSHOT_ATTRIBUTES`, `VSS_SNAPSHOT_STATE`, `VSS_PROVIDER_TYPE`, `VSS_VOLUME_PROP`, `VSS_MGMT_OBJECT_UNION`, and `VSS_MGMT_OBJECT_PROP`.

RPC classes include enumerator `Next` calls, `GetProviderMgmtInterface`, `QueryVolumesSupportedForSnapshots`, `QuerySnapshotsByVolume`, `QueryDiffAreasForVolume`, and `QueryDiffAreasOnVolume`. Wrappers include `IVssEnumMgmtObject`, `IVssEnumObject`, `IVssSnapshotMgmt`, and `IVssDifferentialSoftwareSnapshotMgmt`.

## Control Flow

Wrappers build a request, copy `ORPCthis` from the current class instance, clear ORPC flags, fill method arguments, and send the request with the interface IID and IPID. Methods returning interface pointers wrap returned `abData` in `INTERFACE` and instantiate the proper wrapper. `IVssSnapshotMgmt.GetProviderMgmtInterface` returns `IVssDifferentialSoftwareSnapshotMgmt`; volume and snapshot query methods return enumerator wrappers.

## State and Persistence Behavior

The module has no local durable state. Wrapper instances hold remote interface identity. The remote VSS service may enumerate system volumes, snapshots, providers, or diff areas; these methods are mostly query-oriented in this file and do not create snapshots.

## Dependencies and Integration Points

It depends on Impacket NDR enum/struct/union support, DCOM runtime classes, DCE/RPC primitive types, HRESULT errors, UUID conversion, and `DCERPCException`. It integrates with `dcomrt` activation and `IRemUnknown2` request handling.

## Risks and Edge Cases

Some returned interface pointer joins use `''.join(resp['...']['abData'])`, which is unsafe when `abData` elements are bytes under Python 3. `QuerySnapshotsByVolume` catches `DCERPCException`, prints and hexdumps packet data, then continues as if `resp` exists, which can produce follow-on failures. Only the volume arm of `VSS_MGMT_OBJECT_UNION` is implemented; diff volume and diff area structures are commented out. Remote VSS access is privilege- and configuration-dependent.

## Test Signals

Mocked wrapper tests should verify ORPC fields, IIDs, request classes, and returned wrapper construction. NDR tests should validate VSS GUID alignment and management-object union tags. Integration tests should query supported volumes and diff areas on a controlled Windows host and cover error responses without debug output.
