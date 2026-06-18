# sources/user-network-fs/rclone/bin/test_independence.go

Purpose: standalone diagnostic tool that checks whether integration subtests can pass independently. It runs `go test -v <package>`, extracts `TestIntegration/...` names, then reruns each test individually with `-run`.

Important functions: `findTests` parses verbose test output with regex; `runTest` invokes a targeted test and logs OK/FAILED while printing failing output. State is read-only except build/test caches and any backend test side effects. Dependencies are Go test output format and test package behavior. Risks include regex only matching `TestIntegration/`, full initial suite must pass before independent checks start, and remote tests may mutate shared state. Test signal is the individual rerun status log.
