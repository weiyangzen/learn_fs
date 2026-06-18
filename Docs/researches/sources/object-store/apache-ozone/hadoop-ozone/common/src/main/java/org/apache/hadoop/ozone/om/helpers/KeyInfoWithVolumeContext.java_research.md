# sources/object-store/apache-ozone/hadoop-ozone/common/src/main/java/org/apache/hadoop/ozone/om/helpers/KeyInfoWithVolumeContext.java

Purpose: Wraps `OmKeyInfo` with optional volume context and optional user principal for client-side KMS work such as decrypting encrypted key material.

Important APIs/types/functions: Constructor stores `Optional<OmVolumeArgs>`, `Optional<String>`, and required key info. `fromProtobuf` parses `GetKeyInfoResponse`; `toProtobuf` emits volume info, user principal, and key info using the requested client version. Builder mirrors the fields.

Control flow and state: Optional volume/user fields are only written when present. Key info is always serialized.

State and persistence behavior: Transport wrapper only. It does not persist metadata but contains persistable `OmKeyInfo` and `OmVolumeArgs` protobufs.

Dependencies and integration points: Used by get-key-info RPC paths, especially encrypted-volume flows that require volume owner/KMS principal context. Depends on `OmVolumeArgs`, `OmKeyInfo`, and `GetKeyInfoResponse`.

Risks: Builder does not validate `keyInfo`; a null key causes `toProtobuf` failure. `proto.getUserPrincipal()` returns an empty string when absent, so the optional may be present with an empty value.

Test signals: Round trips with and without volume info, user principal handling, encrypted key path client-version serialization, and null key validation expectations.
