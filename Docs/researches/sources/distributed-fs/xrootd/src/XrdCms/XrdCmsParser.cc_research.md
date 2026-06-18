# sources/distributed-fs/xrootd/src/XrdCms/XrdCmsParser.cc

Purpose: defines CMS request/response serialization schemas and response decoding. It binds `kYR_*` protocol codes to `XrdOucPupArgs` layouts for login, locate/select, prepare, forwarding operations, load, availability, and simple path requests.

Important APIs/functions: static initializer `XrdCmsParseInit` builds PUP argument names; `XrdCmsParser::XrdCmsParser()` populates `vecArgs`; `Decode()` maps manager/redirector responses into `SFS_REDIRECT`, `SFS_STALL`, `SFS_STARTED`, `SFS_DATA`, or `SFS_ERROR`; `mapError(const char *)` and `mapError(int)` translate CMS/string errors to `errno`; `Pack()` serializes a request into iovecs using the selected schema.

Control flow: request schemas are arrays with `Fence`, `End`, `Datlen`, and `EndFill` markers. `Decode()` reads an optional network-order integer followed by message bytes, switches on `hdr.rrCode`, populates `XrdOucErrInfo`, and hijacks oversized data buffers for `SFS_DATA`.

State and persistence: global static parser state includes the PUP name table, PUP instance, schema arrays, vector table, and global `XrdCms::Parser`. No persistent state is written.

Dependencies/integration: depends on `YProtocol.hh` CMS constants, `XrdCmsRRData`, `XrdOucPup`, `XrdOucBuffer`, `XrdOucErrInfo`, and SFS return codes. `XrdCmsProtocol` uses it to parse inbound requests; `XrdCmsResp` uses `Decode()` for asynchronous replies.

Risks: schema and `XrdCmsRRData::ArgName` order must stay synchronized. `Decode()` trusts response header codes and buffer length after minimal checks. Unknown error strings/values collapse to `EINVAL`, which can hide semantic failures. The constructor uses a non-atomic static `Done`, though this is normally initialized during startup.

Test signals: round-trip pack/unpack for every populated `kYR_*` route, malformed payload coverage, large `kYR_data` buffer handoff, and `mapError` coverage for all protocol errors.
