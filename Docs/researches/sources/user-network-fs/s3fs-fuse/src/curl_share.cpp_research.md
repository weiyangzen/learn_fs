<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/s3fs-fuse/src/curl_share.cpp -->
# Research: sources/user-network-fs/s3fs-fuse/src/curl_share.cpp

Purpose: implements per-thread libcurl share handles so S3fsCurl instances can share DNS cache and SSL session cache within a thread while using explicit locks required by libcurl's share API.

Important APIs: `SetDnsCache` and `SetSslSessionCache` toggle which share data types are enabled. `SetCurlShareHandle(CURL*)` obtains or creates the current thread's `CURLSH` and attaches it to an easy handle. `DestroyCurlShareHandleForThread` removes the current thread's share handle and associated locks. Internal callbacks `LockCurlShare` and `UnlockCurlShare` lock DNS or SSL-session mutexes based on `curl_lock_data`.

Control flow: `SetCurlShareHandle` constructs a temporary `S3fsCurlShare`, asks it for a handle tied to `std::this_thread::get_id()`, and sets `CURLOPT_SHARE`. `GetCurlShareHandle` returns an existing per-thread handle from static maps or creates a new `curl_share_init` handle plus lock bundle, initializes lock/unlock/userdata callbacks, enables requested share data, stores both in maps, and returns the raw handle. Initialization tolerates libcurl builds that lack DNS or SSL session sharing by warning and continuing for those options.

State and persistence: static booleans control DNS and SSL cache sharing. Static maps store one `CurlSharePtr` and one `ShareLocksPtr` per thread id, protected by `curl_share_lock`. State is process-local and persists until explicitly destroyed for the thread or process exit.

Dependencies/integration: used by `S3fsCurl::ResetHandle` during handle setup. Depends on libcurl share APIs and `s3fs_logger.h`. The per-thread design avoids sharing the same `CURLSH` across unrelated FUSE threads while still allowing multiple easy handles in one thread to reuse DNS/TLS data.

Risks: cleanup requires `DestroyCurlShareHandleForThread`; otherwise maps can retain entries for dead thread ids in long-running thread-pool churn. Lock callbacks assume `useptr` is a valid `curl_share_locks` for the share lifetime. Only DNS and SSL-session lock data are handled; if future share types are enabled, callbacks must be extended. The temporary object pattern hides the fact that state is static and keyed by thread id.

Test signals: tests should enable/disable DNS and SSL sharing, attach share handles to multiple easy handles in the same thread and different threads, destroy per-thread handles, and simulate libcurl returning `CURLSHE_BAD_OPTION`/`CURLSHE_NOT_BUILT_IN`. Threaded tests should verify no map races under concurrent handle creation and teardown.
<!-- END_FILE_RESEARCH: sources/user-network-fs/s3fs-fuse/src/curl_share.cpp -->
