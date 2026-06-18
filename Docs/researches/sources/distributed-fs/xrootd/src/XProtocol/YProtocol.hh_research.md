<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XProtocol/YProtocol.hh -->
# sources/distributed-fs/xrootd/src/XProtocol/YProtocol.hh

Purpose: defines the XRootD CMS/manager-server "Y" protocol in namespace `XrdCms`. It provides common request/response headers, request codes, response codes, modifiers, error codes, login payload state, and per-operation request skeletons for cluster management, location, staging, load, filesystem state, and redirect coordination.

Important APIs/types/functions: `kYR_Version`, `CmsRRHdr`, `CmsReqCode`, `CmsFwdModifier`, `CmsReqModifier`, `CmsRspCode`, `YErrorCode`, `CmsResponse`, and request structs including `CmsAvailRequest`, `CmsChmodRequest`, `CmsDiscRequest`, `CmsGoneRequest`, `CmsHaveRequest`, `CmsLocateRequest`, `CmsLoginData`, `CmsLoginRequest`, `CmsLoginResponse`, `CmsLoadRequest`, `CmsMkdirRequest`, `CmsMkpathRequest`, `CmsMvRequest`, `CmsPingRequest`, `CmsPongRequest`, `CmsPrepAddRequest`, `CmsPrepDelRequest`, `CmsRmRequest`, `CmsRmdirRequest`, `CmsSelectRequest`, `CmsSpaceRequest`, `CmsStateRequest`, `CmsStatfsRequest`, `CmsStatsRequest`, `CmsStatusRequest`, `CmsTruncRequest`, `CmsTryRequest`, `CmsUpdateRequest`, and `CmsUsageRequest`.

Control flow: no executable code. Runtime CMS control flow is encoded in `rrCode`, `modifier`, `datalen`, and operation-specific option bits. Forwarding behavior is represented by high modifier bits (`kYR_hopcount` and `kYR_hopincr`), with comments naming which operations may be forwarded.

State and persistence behavior: request state is serialized into `CmsRRHdr` plus PUP/string-encoded variable data described in comments. `CmsLoginData` carries persistent cluster identity and capacity state: mode bits, hold time, total/free/min space, filesystem count/utilization, data/subscription ports, server ID, exported paths, interfaces, and environment CGI.

Dependencies: includes `XProtocol/XPtypes.hh`. Comments say binary values use network byte order and variable data is serialized as explained in `XrdOucPup`, so the concrete packing logic lives elsewhere.

Integration points: used by cmsd/managers/supervisors/data servers for namespace location, availability, staging preparation, file operation forwarding, load propagation, status control, and retry/selection decisions. Option bits mirror client-visible behavior such as IPv4/IPv6 preference, private networks, online-only selection, affinity, retry reason, and staging mode.

Risks: header comments say structures need packing for network use, but the structs are not explicitly annotated here; compatibility depends on field choices avoiding padding or being packed by surrounding serializers. Many variable fields are comments rather than C members, so encoder/decoder code must stay in sync with these documented layouts. Modifier bit overlap means new modifiers must preserve hop-count semantics.

Test signals: CMS interoperability tests for login, locate/select, have/gone, load, status, and forwarding; serializer tests for `CmsRRHdr` byte order and `CmsLoginData`; option-mask tests for retry reasons, IP-family return flags, and affinity; negative tests for malformed lengths and unknown request codes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XProtocol/YProtocol.hh -->
