## sources/distributed-fs/xrootd/src/XrdHttp/XrdHttpExtHandler.cc

Purpose: implements `XrdHttpExtReq`, the request summary and response adapter passed to external HTTP extension plugins.

Important APIs and control flow: response helpers delegate to the owning `XrdHttpProtocol`: `SendSimpleResp()`, `StartSimpleResp()`, `SendData()`, `StartChunkedResp()`, `ChunkResp()`, and `BuffgetData()` all return `-1` if no protocol pointer exists. `GetClientID()` asks the underlying `XrdLink` for a client string. `GetSecEntity()` returns the protocol security entity. The constructor copies request verb/resource, references the request header map, injects XRootD-specific synthetic headers for query/fullresource/protocol, extracts client DN/host/groups from `SecEntity`, and exposes packet marking, SciTag, Repr-Digest, Want-Repr-Digest, credential forwarding, and request length.

State and persistence: `XrdHttpExtReq` stores request snapshot fields plus a reference to the original header map; modifying `headers` can affect the request's header map. No durable state is written.

Dependencies and integration: bridges `XrdHttpReq`, `XrdHttpProtocol`, `XrdLink`, `XrdSecEntity`, and plugin code implementing `XrdHttpExtHandler`. It is built into `XrdHttpUtils` for plugins.

Risks and test signals: `StartSimpleResp()` ignores its `keepalive` argument and passes `true`, which should be verified against intended API. Header reference lifetime depends on the original request. Tests should cover null-protocol guards, synthetic headers, security field trimming, chunked response lifecycle, body buffering with wait/no-wait, and digest map propagation to plugins.
