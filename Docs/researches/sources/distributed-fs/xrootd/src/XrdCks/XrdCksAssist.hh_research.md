# sources/distributed-fs/xrootd/src/XrdCks/XrdCksAssist.hh

Purpose: declares checksum xattr helper functions that convert between external algorithm/value strings and the serialized `XrdCksData` xattr representation.

Important APIs: `XrdCksAttrData()` returns raw bytes suitable for setting an xattr. `XrdCksAttrName()` returns the xattr key name. `XrdCksAttrValue()` converts a raw xattr payload back into a hex checksum string.

Control flow and integration: callers use these helpers around xattr operations, usually with `XrdSysXAttr` or OSS-backed checksum managers. The header documents expected inputs and error reporting through `errno`.

State and persistence: no state, but the helpers define the persistent wire/storage format for XRootD checksum metadata.

Dependencies: includes `<ctime>`, `<string>`, and `<vector>`.

Risks and test signals: API tests should verify buffer length expectations and that callers handle empty return values by consulting `errno`.
