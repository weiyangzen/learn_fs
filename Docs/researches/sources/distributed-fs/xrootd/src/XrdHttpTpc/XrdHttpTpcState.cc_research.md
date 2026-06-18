# sources/distributed-fs/xrootd/src/XrdHttpTpc/XrdHttpTpcState.cc

Purpose: Implements libcurl callback state for individual HTTP TPC HEAD, pull, and push transfers.

Important APIs/types/functions: Destructor frees curl header lists. `InstallHandlers` sets user agent, header callbacks, read/write callbacks, redirect/auth options, upload mode, low-speed limits, and push size. `SetupHeaders` and `SetupHeadersForHEAD` forward copy/transfer headers and digest negotiation. `Header`, `WriteCB`, `PushRespCB`, `ReadCB`, `Write`, `Read`, `Flush`, `Finalize`, `Duplicate`, `SetTransferParameters`, and `GetConnectionDescription` implement transfer behavior.

Control flow: Curl delivers headers first; `Header` parses status, content length, and `Repr-Digest`. Pull write callbacks reject body before headers, collect up to 1KB of remote error body for >=400 statuses, or write to the local `Stream`. Push read callbacks read from the local stream after successful remote status. Duplicates copy curl options and custom header lists for multistream range transfers. Finalization delegates to `Stream`.

State and persistence: Tracks per-request offset, start offset, status code, error code/message, content length, push length, header state, curl handle, header list, protocol string, transfer-state flag, credential-forwarding flag, and parsed repr digests. Durable effects occur via `Stream` read/write/close.

Dependencies and integration points: Uses libcurl easy options and callbacks, `XrdSfsFile` via `Stream`, `XrdHttpExtReq`, `XrdHttpHeaderUtils::parseReprDigest`, and XrdVersion for user agent.

Risks: `Move` copies most fields but assigns `other.m_repr_digests = m_repr_digests`, which appears reversed from normal move semantics and could lose digest state in the moved-to object if ever relevant. `SetupHeaders` calls `curl_slist_append(list, reprDigestHeader.c_str())` without assigning the return value in the push digest branch, so that appended header may be dropped. Header parsing returns zero on malformed input, causing curl aborts. Manual curl-slist ownership is delicate.

Test signals: HEAD content-length and repr-digest parsing, push and pull error-body capture, copy-header/transferheader forwarding, Want-Repr-Digest formation, duplicate handles retaining headers, range setup, IPv6 connection description formatting, and finalization error propagation.
