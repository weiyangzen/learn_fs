# sources/distributed-fs/xrootd/src/XrdSecsss/XrdSecsssEnt.cc

Purpose: serializes `XrdSecEntity` identity data into SSS record/response data blocks and owns per-entity contact cleanup state.

Important APIs and functions: `AddContact()`, `Delete()`, `RR_Data()`, `Serialize()`, and static `setHostName()`. Local `copyAttrs` walks `XrdSecEntityAttr` key/value pairs twice: first for sizing, then for packing.

Control flow: construction optionally serializes an entity. `Serialize()` computes V1 identity size, pads small payloads with random data, computes V2 extras, includes protocol, trace ID, uid/gid names for cloned protocols, entity attributes, capabilities, and optional credentials. `RR_Data()` lazily serializes if needed, prepends client IP and cached hostname, selects V1 or V2 payload length, and returns a malloc-owned buffer.

State and persistence: per-object state includes packed `eData`, V1 length, total V2 length, credential length, source entity pointer, reference count, and contact set. Static state caches packed local hostname. No disk persistence.

Dependencies and integration: uses `XrdOucPup` packing, `XrdOucUtils` uid/gid lookup, `XrdSecEntity`, `XrdSecEntityAttr`, `XrdSecsssRR`, `XrdSecsssKT::genKey`, and optional `XrdSecsssCon` cleanup.

Risks: `RR_Data()` computes `strlen(hostIP)` before checking for null, so callers must pass a non-null IP despite later conditional code. Deferred serialization requires the original `XrdSecEntity` to remain valid. Manual packed-size math must stay in sync with wire constants.

Test signals: serialize minimal and full entities, V1/V2 option combinations, credentials at and above `MaxCSz`, entity attributes, non-sss underlying protocols, null/empty host handling, and cleanup callback invocation.
