# sources/distributed-fs/xrootd/src/XrdCks/XrdCksAssist.cc

Purpose: implements helper functions for encoding and decoding XRootD checksum extended attributes.

Important APIs: `XrdCksAttrData(cstype, csval, mtime)` validates checksum type/name length and known hex-string lengths, fills an `XrdCksData` object, sets file mtime and checksum age, and returns its raw bytes as `std::vector<char>`. `XrdCksAttrName(cstype, nspfx)` lowercases the type and returns names like `XrdCks.adler32`, optionally prefixed. `XrdCksAttrValue(cstype, csbuff, csblen)` validates a raw `XrdCksData` blob and returns the checksum value as hex.

Control flow: a static checksum table maps known algorithms to hex and binary lengths. `LowerCase()` bounds-checks against destination length. Errors are reported by setting `errno` and returning an empty vector/string.

State and persistence: helpers are stateless, but their serialized `XrdCksData` layout is the persistent xattr value format.

Dependencies and integration: depends on `XrdCksData.hh` and standard string/time utilities. Used by checksum xattr consumers to maintain consistent xattr names and binary values.

Risks and test signals: tests should cover known and unknown algorithms, uppercase input normalization, namespace prefixes with/without trailing dots, malformed binary blobs, stale length fields, and errno values (`ENAMETOOLONG`, `EINVAL`, `EOVERFLOW`, `EMSGSIZE`, `ENOENT`).
