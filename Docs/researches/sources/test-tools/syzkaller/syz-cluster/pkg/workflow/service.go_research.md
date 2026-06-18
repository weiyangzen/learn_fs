## sources/test-tools/syzkaller/syz-cluster/pkg/workflow/service.go

This file defines the workflow abstraction used by syz-cluster to start and monitor patch-series workflows. `Service` has `Start`, `Status`, and `PollPeriod`. `Status` is a string enum with `not_found`, `running`, `finished`, and `failed`.

`MockService` is a test helper with a mutex around `OnStart` and `OnStatus` callbacks so tests can deterministically serialize workflow callback behavior. Default `Start` succeeds, default `Status` returns `StatusNotFound`, and `PollPeriod` returns the configured delay.

The interface isolates controller/service code from Argo. There is no persistent state except callback-controlled mock state in tests. Risks are limited: callers must interpret `StatusNotFound` correctly and mock callbacks can still encode arbitrary behavior. The typo in the comment ("dong boot tests") is non-functional.
