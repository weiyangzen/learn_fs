## sources/test-tools/syzkaller/syz-cluster/reporter-server/main.go

This is the reporter-server entrypoint. It initializes the syz-cluster app environment, starts a background `reporter.Generator` loop, creates a reporter API server, and serves its mux on `:8080`.

The process has two major flows: background report generation and synchronous HTTP handling. `context.Background()` is shared and there is no explicit shutdown handling in this file. Dependencies are `pkg/app` for configuration/environment and `pkg/reporter` for generation/API logic.

Persistent state is handled by downstream repositories and blob/email integrations in the reporter package. Risks include fatal process exit on HTTP server failure, no graceful shutdown, and generator lifecycle tied only to process lifetime. Test coverage is expected in the reporter package rather than the entrypoint.
