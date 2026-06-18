# sources/user-network-fs/samba/source4/libnet/libnet_become_dc.h

## Purpose
`libnet_become_dc.h` defines the public request, metadata, partition, chunk, and callback types consumed by `libnet_BecomeDC`. It is the contract between the generic libnet promotion orchestrator and the caller that validates options, prepares the local database, and stores replicated schema/config/domain chunks.

## Important APIs, Types, And Functions
`struct libnet_BecomeDC` is the top-level API object. Inputs include domain DNS/NetBIOS/SID, source DSA address, destination DSA NetBIOS name, callback table, and `rodc_join`. Output currently exposes `error_string`.

`struct libnet_BecomeDC_Domain`, `Forest`, `SourceDSA`, and `DestDSA` split caller input from constructed promotion metadata. Constructed fields include DNs, GUIDs, behavior versions, schema version, site GUID, computer/server/NTDS DNs, invocation ID, and account-control value.

`struct libnet_BecomeDC_Partition` describes a replicated naming context and tracks source/destination DSA GUIDs, source invocation ID, high-watermark, `more_data`, replica flags, and a `store_chunk` callback. `struct libnet_BecomeDC_StoreChunk` is the callback payload containing the promotion metadata, partition, original request pointers for levels 5/8/10, response pointers for counters 1/6, and the GENSEC session key.

`struct libnet_BecomeDC_Callbacks` supplies optional `check_options`, `prepare_db`, `schema_chunk`, `config_chunk`, and `domain_chunk` callbacks plus private data.

## Control Flow
The header mirrors the phases in the C file: discovery populates `Domain`, `Forest`, and `SourceDSA`; pre-mutation validation uses `CheckOptions`; DRS add-entry and local initialization use `PrepareDB`; replication uses the partition and chunk types. Callbacks return `NTSTATUS` or `WERROR`, allowing the orchestrator to abort when caller validation, local preparation, or storage fails.

## State And Persistence Behavior
The header does not persist data itself, but it defines the data passed to persistence callbacks. `prepare_db` is the hook for creating local database structures before replication, and each chunk callback is expected to persist replicated objects. The callback payload pointers are owned by the active promotion state, so consumers must copy any data they need beyond the callback lifetime.

## Dependencies And Integration Points
The file includes DRSUAPI generated declarations and references Samba security/domain types such as `dom_sid`, `GUID`, `DATA_BLOB`, `NTSTATUS`, and `WERROR`. It is included by libnet users that need domain-controller promotion and by the implementation file.

## Risks
Because the API exposes internal request/response pointers in `StoreChunk`, callers can accidentally retain short-lived memory or couple tightly to DRSUAPI levels. The top-level output has only `error_string`, while the implementation primarily reports through status. The callback contract must be honored carefully: returning success without durable storage may allow the promotion sequence to continue even though local replication state is incomplete.

## Test Signals
Compile-time tests should catch DRSUAPI type drift. Integration tests should verify callbacks receive populated domain/forest/source/destination metadata, correct partition DNs and high-watermarks, and correct RODC-vs-writable metadata across schema, config, and domain chunks.
