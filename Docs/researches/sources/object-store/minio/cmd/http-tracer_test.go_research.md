# sources/object-store/minio/cmd/http-tracer_test.go

## Purpose

`http-tracer_test.go` verifies LDAP password query redaction and adds concurrency tests for the HTTP stats types defined in `http-stats.go`. The file acts as a regression suite for trace sanitization and for prior data races in shared HTTP metric maps.

## Important Tests And Control Flow

`TestRedactLDAPPwd` checks empty input, LDAP password in the middle, beginning, and end of a query string, plus a non-LDAP query that should remain unchanged. The expected output preserves all non-password segments and replaces only the password value. The regex therefore needs to handle both prefixed and suffix-only query fragments, not just canonical URL-encoded query parsing.

`TestRaulStatsRaceCondition` creates a `HTTPStats`, launches many writer goroutines that call `updateStats` and direct `HTTPAPIStats.Inc`, and many reader goroutines that call `toServerHTTPStats` and `Load`. It asserts that some total requests survive concurrent activity. `TestRaulHTTPAPIStatsRaceCondition` stresses `HTTPAPIStats.Inc` while readers call `Load`, then asserts no increments were lost for a single API key. `TestRaulBucketHTTPStatsRaceCondition` repeatedly pairs active bucket request updates with response-completion updates and loads bucket stats.

## State, Dependencies, Integration, Risks, And Signals

The tests use goroutines, `sync.WaitGroup`, microsecond sleeps, and `xhttp.ResponseRecorder`. Their strongest signal appears when run with Go's `-race`; without race detection, they still catch obvious lost updates for `HTTPAPIStats`. They cover nil-recorder active request flow and response-recorder completion flow for bucket stats. Gaps remain around `httpTracerMiddleware` end-to-end publication, trace body redaction, status 499 classification, Prometheus histogram side effects, and active-request decrement balance on panic or early return paths.
