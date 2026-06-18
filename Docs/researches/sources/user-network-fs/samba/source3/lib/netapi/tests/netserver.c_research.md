# Research: sources/user-network-fs/samba/source3/lib/netapi/tests/netserver.c

Purpose: integration tests for `NetServerGetInfo` levels. It verifies that the server info query path can be called for common LANMAN/SRVSVC levels.

Important APIs/functions: `netapitest_server` iterates levels 100, 101, 102, 402, 403, 502, 503, and 1005, calls `NetServerGetInfo`, and treats status 124 as tolerated not-implemented behavior.

Control flow: the test is a simple fail-fast loop. Each level allocates a local `buffer` pointer, calls the API, and aborts on errors other than 124. It does not inspect or free returned buffers in the visible code, so it primarily checks call success.

State and persistence: read-only target interaction. No server configuration is changed. Any allocated output should be freed for leak cleanliness, but this test does not call `NetApiBufferFree`.

Dependencies/integration: uses public `NetServerGetInfo` declarations and shared `ARRAY_SIZE`/status macros. It is run near the end of `netapitest.c`.

Risks: the test includes level 403 even though `serverinfo.c` remote validation rejects it, relying on tolerated status 124. Lack of field validation can miss mapping regressions. Missing buffer free may show up under leak detectors if the process lifetime is extended or many runs happen in-process.

Test signals: strengthen by checking expected server name/comment/version fields for levels 100/101/102/1005, freeing buffers, explicitly asserting unsupported levels, and adding `NetServerSetInfo` tests in a disposable registry-backed configuration.
