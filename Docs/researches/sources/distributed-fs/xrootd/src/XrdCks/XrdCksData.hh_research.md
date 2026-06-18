# sources/distributed-fs/xrootd/src/XrdCks/XrdCksData.hh

Purpose: defines `XrdCksData`, the fixed-size checksum record passed through manager APIs and serialized into xattrs.

Important APIs and fields: constants `NameSize` and `ValuSize` bound algorithm names and binary values. Fields store `Name`, unioned `fmTime`/`envP`, `csTime`, reserved bytes, `Length`, and `Value`. Operators compare name, length, and value. `Get()` renders the binary value as lowercase hex. `Set(const char*)` sets the algorithm name; `Set(const void*, int)` sets binary value; `Set(const char*, int)` parses hex text. `Reset()` clears the record and constructor calls it. `HasValue()` checks whether the value buffer begins with a nonzero byte.

Control flow and integration: manager calls use `Name` as input and fill `Value`/time fields as output. Assist helpers serialize the whole struct to xattrs, so layout compatibility matters.

State and persistence: the object is both in-memory API state and persistent xattr payload. The `fmTime`/`envP` union means the same storage has different meanings depending on operation direction.

Dependencies: includes `<cstring>` and forward-declares `XrdOucEnv`.

Risks and test signals: tests should cover max name/value lengths, invalid hex, odd-length hex rejection, zero-valued valid checksums versus `HasValue()`, struct-size compatibility, and comparison semantics.
