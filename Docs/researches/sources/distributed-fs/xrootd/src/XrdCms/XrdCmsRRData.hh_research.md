# sources/distributed-fs/xrootd/src/XrdCms/XrdCmsRRData.hh

Purpose: declares POD-style containers for parsed CMS request data and redirector login data.

Important APIs/types: `XrdCmsRLData` holds auth/SID/path strings and total length. `XrdCmsRRData` contains the request header, parsed string fields for operation arguments, options, path length, disk/load values, a union for `dskUtil`/`waitVal`, backing buffer metadata, routing flags, `ArgName` enum used by parser schemas, static `Objectify()`, `getBuff()`, and free-list `Next`.

Control flow: parser schemas fill fields by offset into this POD. Protocol dispatch reads headers/payloads into `Buff`, then `XrdCmsParser` points fields into that buffer.

State and persistence: object state is transient and mostly references the owned buffer. Comments intentionally omit constructors/destructors so the type behaves like POD for `XrdOucPup`.

Dependencies/integration: includes `YProtocol.hh` for CMS headers/constants. `ArgName` must align with `XrdCmsParser` PUP name definitions.

Risks: POD design means no automatic cleanup of `Buff`; ownership is manual. String fields become invalid if `Buff` is freed or stolen. Adding fields can break parser offset assumptions.

Test signals: schema offset/ArgName sync tests, memory sanitizer tests for buffer lifetime, and compile warnings around POD assumptions.
