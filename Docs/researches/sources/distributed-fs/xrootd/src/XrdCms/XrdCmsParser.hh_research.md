# sources/distributed-fs/xrootd/src/XrdCms/XrdCmsParser.hh

Purpose: declares the CMS parser facade around `XrdOucPup`. It exposes static helpers for decoding redirector responses, mapping errors, packing outbound requests, and parsing login/general request payloads.

Important APIs/types: `Decode()`, both `mapError()` overloads, `Pack()`, `Parse(CmsLoginData *)`, `Parse(int, ..., XrdCmsRRData *)`, static `Pup`, `PupArgs()`, and the global `XrdCms::Parser`. Private static schema arrays map protocol request codes to unpacking layouts.

Control flow: inline `Parse()` zeros selected pointer fields before unpacking so recycled POD objects do not retain stale pointers. `PupArgs()` bounds-checks request codes before indexing `vecArgs`.

State and persistence: all parser schemas are static and process-wide. Parsed string pointers reference the request buffer owned by `XrdCmsRRData`; no copies are made here.

Dependencies/integration: includes `YProtocol.hh`, `XrdCmsRRData.hh`, and `XrdOucPup.hh`. It is embedded in `XrdCmsProtocol` as `ProtArgs` and exported as `XrdCms::Parser`.

Risks: parse success depends on caller-owned buffers living long enough. `rnum` is checked only against the upper bound, not negative values, though protocol codes are normally unsigned/small. Adding a new CMS request requires updating this header and the `.cc` schema vector.

Test signals: static analyzer checks for negative indexing risk, tests for recycled `XrdCmsRRData` pointer reset, and compilation coverage when `kYR_MaxReq` or `ArgName` changes.
