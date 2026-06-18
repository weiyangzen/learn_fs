# sources/object-store/openstack-swift/swift/common/direct_client.py

Purpose: provides low-level helpers for Swift internal tools and daemons to call account, container, object, replication, and recon servers directly, bypassing the proxy path.

Important APIs/types/functions: `DirectClientException` and `DirectClientReconException` wrap failed backend responses with host, device, status, reason, and headers. `_make_req` is the common request/send/read helper for most methods. `_get_direct_account_container` implements JSON listings. `gen_headers` adds direct-client user agent and reserved-name allowance. Public helpers include `direct_get_account`, container CRUD/listing methods, object HEAD/GET/PUT/POST/DELETE, `direct_get_suffix_hashes`, `direct_get_recon`, and `retry`.

Control flow: path helpers quote Swift path components, `get_ip_port` selects normal or replication network endpoint from node/header inputs, and `http_connect` or `http_connect_raw` opens the backend connection under connect timeout. `_make_req` handles optional bodies by setting `Content-Length` or chunked transfer encoding, streams body chunks under send timeout, reads the full response under response timeout, and raises on non-2xx statuses. Listing helpers force `format=json`, add marker/limit/prefix/delimiter/end_marker/reverse parameters, and return `HeaderKeyDict` plus decoded JSON or empty listing on 204. `retry` retries socket, HTTP, timeout, and retryable 5xx client exceptions with exponential backoff, but not 507.

State and persistence: no durable state; side effects are backend HTTP operations that create/update/delete Swift DB and object state. Request defaults add current timestamps and reserved-name headers.

Dependencies and integration: depends on Swift buffered HTTP connections, eventlet-style timeouts, ring node dicts, `HeaderKeyDict`, `Timestamp`, `FileLikeIter`, pickle loading for suffix hashes, and Swift HTTP status helpers. It is used by replication, dispersion, recon, and operational code needing direct storage-node access.

Risks: direct calls bypass proxy middleware and must provide correct backend headers; GET with `resp_chunk_size` returns a generator tied to an open response; `_make_req` drains responses before returning, so it is not suitable for streaming reads; chunked request body framing must remain exact; retry can amplify load during outages. Tests should cover query duplicate detection, header normalization, chunked and fixed-length PUTs, exception metadata, replication-network suffix hash calls, retry stop conditions, and recon JSON failures.
