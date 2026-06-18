# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/service/OpenKeyCleanupService.java

Purpose: `OpenKeyCleanupService` is a single-threaded OM background service that cleans expired open-key metadata. It deletes abandoned non-hsync open keys and commits expired hsync keys so client-side lease loss does not leave indefinite metadata or block namespace accounting.

Important APIs and types: the constructor reads open-key expiration, lease hard/soft limits, and per-task cleanup limit from configuration. Test hooks include `suspend()`, `resume()`, and `getSubmittedOpenKeyCount()`. `getTasks()` returns two `OpenKeyCleanupTask` instances, one for `BucketLayout.DEFAULT` and one for `BucketLayout.FILE_SYSTEM_OPTIMIZED`.

Control flow: each task requires `!suspended` and `ozoneManager.isLeaderReady()`. It calls `keyManager.getExpiredOpenKeys(expireThreshold, cleanupLimitPerTask, bucketLayout, leaseThreshold)`, counts expired non-hsync keys grouped into `OpenKeyBucket` builders, submits a single `DeleteOpenKeys` OM request for those groups, then individually submits `CommitKey` requests for hsync builders. Successful responses update OM metrics for cleaned and hsync-cleaned open keys, record performance latency, and add to `submittedOpenKeyCount`.

State and persistence behavior: the service never mutates RocksDB tables directly. It submits Ratis-backed `OMRequest`s with a service-owned random `ClientId` and monotonically increasing `callId`, letting normal OM request handlers apply table mutations. This protects leader/follower consistency and keeps cleanup idempotent if a key is committed or removed between scan and request execution.

Dependencies and integration points: it depends on `KeyManager` for expiration scanning, `ExpiredOpenKeys` for split non-hsync/hsync results, `OzoneManagerRatisUtils` for submission, and OM metrics/perf metrics for observability. It is integrated through key-manager service startup and handles both OBS and FSO layouts explicitly.

Risks: the constructor throws if the hard lease limit is below the soft limit, making misconfiguration fail early. Cleanup is bounded by `cleanupLimitPerTask`, but both layout tasks run each cycle, so aggregate work can be twice the configured limit. Hsync commit requests are submitted one at a time, which is simple but potentially expensive under many expired hsync keys. The service logs and retries later on scan or Ratis submission failure.

Test signals: `TestOpenKeyCleanupService`, `TestHSync`, `TestHSyncUpgrade`, `TestOzoneShellHA`, and multipart-abort tests cover expired-key deletion, hsync commit handling, recovery-flag cases, service suspension, and interactions with client-visible lease behavior.
