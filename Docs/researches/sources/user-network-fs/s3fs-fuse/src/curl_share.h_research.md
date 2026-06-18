<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/s3fs-fuse/src/curl_share.h -->
# Research: sources/user-network-fs/s3fs-fuse/src/curl_share.h

Purpose: declares the `S3fsCurlShare` helper that manages libcurl `CURLSH` share handles and their lock bundles for DNS and SSL session reuse.

Important APIs/types: `curl_share_locks` contains separate mutexes for DNS and SSL session data. `CurlSharePtr` and `ShareLocksPtr` are unique pointers with libcurl cleanup semantics. `S3fsCurlShare` exposes static toggles `SetDnsCache`, `SetSslSessionCache`, `SetCurlShareHandle`, and `DestroyCurlShareHandleForThread`.

Control flow surface: external code never directly owns `S3fsCurlShare` state. `SetCurlShareHandle` creates a short-lived object to use the current thread id, then private methods create/find the thread's persistent share handle. Private callbacks satisfy libcurl's lock/unlock contract and `InitializeCurlShare` wires callbacks/userdata/share types.

State and persistence: declares static process-wide maps from `std::thread::id` to share handles and lock structures, protected by `curl_share_lock`. Each object instance stores only the current thread id. State is in-memory and should be cleaned when a worker thread is done.

Dependencies/integration: includes libcurl, STL map/memory/mutex/thread, and `common.h` for lock annotations. Integrated by `S3fsCurl::ResetHandle` to set `CURLOPT_SHARE` on each easy handle.

Risks: map lifetime and thread-id reuse need care if worker threads are short-lived. The `NO_THREAD_SAFETY_ANALYSIS` callbacks bypass clang checking because libcurl controls the call boundary. If libcurl invokes callbacks after cleanup due to misuse, `useptr` would dangle.

Test signals: compile with clang annotations, verify one share handle per thread, verify cleanup removes both maps, and run a multithreaded smoke test using easy handles with DNS/SSL sharing enabled.
<!-- END_FILE_RESEARCH: sources/user-network-fs/s3fs-fuse/src/curl_share.h -->
