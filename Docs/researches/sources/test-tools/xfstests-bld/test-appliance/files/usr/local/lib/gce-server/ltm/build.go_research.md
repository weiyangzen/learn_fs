# sources/test-tools/xfstests-bld/test-appliance/files/usr/local/lib/gce-server/ltm/build.go

Purpose: LTM-to-KCS forwarding helper for build and bisect requests.

Important API: `ForwardKCS(req server.TaskRequest, testID string)` creates an LTM log directory, initializes a log file, defers failure email, and calls `server.SendInternalRequest(req, log, true)`.

State and dependencies: writes `/var/log/go/ltm_logs/<testID>/run.log`; depends on `util/server` for internal HTTPS request delivery, `util/email` for panic reports, and `util/logging`.

Integration points: called by LTM `runTests` for user `--commit`, watch, and bisect flows; called by mock sharder when reporting bisect step results.

Risks and test signals: failures in KCS reachability surface through panic/failure email. The helper is intentionally thin, so tests focus on request fields set by callers and `SendInternalRequest` behavior.
