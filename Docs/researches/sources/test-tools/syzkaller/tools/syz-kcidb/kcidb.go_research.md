# sources/test-tools/syzkaller/tools/syz-kcidb/kcidb.go

Purpose: `syz-kcidb` converts a syzbot dashboard bug report into KCIDB data and either publishes it to KCIDB or writes it to a JSON file.

Important APIs and flow: `main` parses KCIDB REST/token, dashboard client/address/key, bug ID, input file, and output file flags. It reads a `dashapi.BugReport` from `-input` JSON when supplied, otherwise loads it from dashboard via `dashapi.New` and `LoadBug`. It enables `kcidb.Validate`, creates a KCIDB client with origin `syzbot`, defers close, then calls `PublishToFile` when `-output` is set or `Publish` otherwise.

State and persistence: reads optional bug JSON, writes optional KCIDB JSON, or publishes to the REST API. No other local state.

Dependencies and integration: depends on dashboard API types, `pkg/kcidb`, context, and `tool.Fail`.

Risks: constants for project/topic are defined but unused in this file. Missing flags are not locally validated and will fail in downstream clients. Publishing is high-impact remote state.

Test signals: no direct test. File-output mode is the safest integration test path because it exercises conversion without remote submission.
