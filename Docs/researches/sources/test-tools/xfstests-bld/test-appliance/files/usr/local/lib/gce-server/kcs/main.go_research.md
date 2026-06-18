# sources/test-tools/xfstests-bld/test-appliance/files/usr/local/lib/gce-server/kcs/main.go

Purpose: HTTPS entrypoint for the Kernel Compile Server.

Important endpoints: `/gce-xfstests` accepts authenticated user build requests; `/internal` accepts password-protected LTM internal requests; `/internal-status` returns active bisectors to LTM. `runCompile` parses `TaskRequest`, assigns or reuses test IDs, routes plain builds, LTM builds, and bisect start/step requests. `status` wraps `BisectorStatus`.

Control flow: create `server.Instance` on `:443`; register handlers with `LoginHandler` for user endpoint and `FailureHandler` for panic-to-JSON handling; start `StartTracker` in a goroutine, start TLS server, and block on tracker completion.

State and dependencies: relies on shared server package for TLS, auth, session cookies, and internal password validation. It uses `mymath.GetTimeStamp` for generated IDs and KCS build/bisect package globals for active work.

Risks and test signals: request handling immediately starts goroutines and returns success before build/test completion. Panics are converted to JSON for request setup failures but asynchronous worker failures are reported through logs/email. Endpoint tests should cover routing for user, LTM build, bisect start/step, and invalid requester.
