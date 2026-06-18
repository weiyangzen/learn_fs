# sources/distributed-fs/xrootd/src/XrdHttpTpc/XrdHttpTpcTPC.cc

Purpose: Implements the HTTP TPC extension handler that processes `COPY` and `OPTIONS`, performs pull/push transfers via libcurl and SFS, emits progress markers, handles redirects, and reports monitoring.

Important APIs/types/functions: Static plugin entry `XrdHttpGetExtHandler`, `TPCHandler` constructor/destructor, `MatchesPath`, `ProcessReq`, `ProcessOptionsReq`, `ProcessPullReq`, `ProcessPushReq`, `RunCurlWithUpdates`, `SendPerfMarker`, `PerformHEADRequest`, `GetRemoteFileInfoTPCPull`, `RedirectTransfer`, `OpenWaitStall`, `ConfigureCurlCA`, socket/SSL callbacks, `mismatchReprDigest`, `GetAuthz`, `prepareURL`, and `logTransferEvent`.

Control flow: `ProcessReq` rejects unsupported credential modes, chooses pull on `Source` and push on `Destination`, normalizes `davs/s3/s3s` source schemes to HTTPS, and only allows HTTP(S). Pull initializes curl, optionally binds fixed route interface, opens local file for write with `oss.task=httptpc` and `oss.asize`, fetches remote HEAD info and repr digests, verifies client-provided digest, then streams single or multistream. Push opens local file read-only, handles filesystem redirects, uploads to remote, and streams progress. Both modes use chunked 202 responses with periodic performance markers and final success/failure text.

State and persistence: Static state includes monitor ID, marker period, block sizes, mutex, and CRL policy. Per-transfer `TPCLogRecord` captures local/remote URLs, user, stream count, status, bytes, IP version, PMark manager, and reports to `XrdXrootdTpcMon` on destruction. Durable effects are local file create/truncate/write for pull and remote upload for push.

Dependencies and integration points: Integrates XrdHTTP extension ABI, XRootD SFS, `XrdSecEntity`, `XrdXrootdRedirHelper`, `XrdXrootdTpcMon`, `XrdNetUtils`, `XrdTlsTempCA`, libcurl, OpenSSL, PMark, HTTP utils, and TPC state/stream utilities.

Risks: Network callbacks enforce private/local address policy but depend on libcurl using the custom open socket path. `allowMissingCRL` disables a CRL failure in the OpenSSL verify callback only for a specific error. `m_monid++` in pull is not protected by the mutex unlike push. Redirect URL construction must preserve full resource query and encode xrootd opaque data correctly. `OpenWaitStall` breaks after a single stall/started sleep rather than looping to retry multiple times.

Test signals: COPY pull/push happy paths, unsupported credential and missing source/destination, scheme filtering, local/private address blocking, SFS redirect with and without redirect plugin rewrite, fixed-route interface, HEAD failures, digest mismatch 412, CRL/no-CRL CA behavior, chunked progress markers, timeout on no progress, remote HTTP errors, and monitor record output.
