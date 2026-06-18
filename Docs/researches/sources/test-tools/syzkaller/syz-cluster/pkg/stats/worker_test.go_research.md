## sources/test-tools/syzkaller/syz-cluster/pkg/stats/worker_test.go

`TestWorker` is an integration-style test for the stats worker using a test app environment, controller test server, real repositories, and fake series/findings. It verifies the prevented-bugs aggregation and old-version reset behavior.

The test creates a first series with findings, uploads a patched-target passed test step tied to one finding, confirms no stats row exists before `RunOnce`, then expects one prevented bug. It creates a second version with two passed patched steps referring to the same finding across two test names, runs the worker again, and expects the first series stat to be zeroed while the second has one prevented bug. Finally it validates `PreventedBugsPerMonth` returns one series and one bug.

This is the key test signal for `pkg/stats/worker.go` and its repository queries. It exercises controller upload APIs, finding repository reads, session-test and test-step persistence, stats upsert, previous-version discovery, and monthly aggregation. Risks not fully covered include worker loop timing/cancellation and error logging paths.
