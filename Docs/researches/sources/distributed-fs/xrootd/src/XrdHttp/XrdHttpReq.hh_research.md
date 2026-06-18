# sources/distributed-fs/xrootd/src/XrdHttp/XrdHttpReq.hh

Purpose: Declares `XrdHttpReq`, the main HTTP/WebDAV request object used by `XrdHttpProtocol` to parse HTTP input, hold request metadata, drive XRootD bridge operations, and translate asynchronous bridge callbacks into HTTP responses.

Important APIs/types/functions: `ReqType` enumerates supported verbs and is explicitly tied to monitoring verb counter order. The class inherits `XrdXrootd::Bridge::Result` and overrides `Data`, `Done`, `Error`, `File`, and `Redir`. Public parser and execution entry points are `parseFirstLine`, `parseLine`, `parseBody`, `ProcessHTTPReq`, `ReqReadV`, multipart header builders, `appendOpaque`, `addCgi`, and transfer-status helpers. Request state includes resource strings, opaque env, headers, host/destination, digest maps, checksum handler pointers, range handling, xrootd request/response fields, file metadata, monitoring state, scitag, and chunk/trailer flags.

Control flow: Header/body parsing populates the fast-access fields, then `ProcessHTTPReq` issues xrootd bridge operations according to `reqstate`. Bridge callbacks place response data into `iovP/iovN/iovL/final`, map errors and redirects, and call post-processing helpers. GET handling is split between open/stat header emission, directory listing post-processing, single-range/multipart response streaming, footer error handling, and optional digest/checksum headers. PUT and write flows use `length`, `writtenbytes`, `m_appended_asize`, and opaque construction to coordinate with the bridge.

State and persistence: The class is per-request but long-lived across asynchronous callbacks. It persists current HTTP status, first emitted status, request headers, opaque values, file handle bytes, chunk offsets, checksum results, and monitoring timestamps until `reset()` or destruction. No durable storage is owned here; persistence is in the backend xrootd/SFS layer.

Dependencies and integration points: Integrates `XProtocol`, `XrdXrootdBridge`, `XrdOucEnv/String`, checksum and range handlers, `XrdHttpProtocol`, and `XrdHttpMonState`. `appendOpaque` and `addCgi` connect HTTP metadata to xrootd opaque arguments. `ReqType` and `monState` feed monitoring.

Risks: This header exposes many mutable public fields, so state-machine invariants are distributed across implementation files. Header parsing must enforce RFC `Content-Length` rules and avoid duplicate/ambiguous length handling. Any change to `ReqType` must be synchronized with monitoring schemas. Late I/O errors after response start rely on trailers/footers and can otherwise be hard to report correctly.

Test signals: Exercise malformed headers, duplicate content lengths, all supported verbs, single and multipart ranges, directory listings, chunked/trailer status, redirects, checksum/digest negotiation, bridge error mappings, and keepalive reset behavior.
