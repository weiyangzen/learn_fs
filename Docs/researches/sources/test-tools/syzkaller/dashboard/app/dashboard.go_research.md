# sources/test-tools/syzkaller/dashboard/app/dashboard.go

Purpose: production entry point for the App Engine dashboard binary.

Important APIs and functions: `enableProfiling` starts Google Cloud Profiler with default App Engine-inferred service metadata and logs failures through syzkaller's logging package. `main` calls `enableProfiling`, installs `mainConfig`, and hands control to `appengine.Main`.

Control flow: startup is deliberately minimal. Config installation is the heavy initializer: it validates config, registers HTTP/API/cron handlers, and initializes integrations. After that, App Engine serves requests.

State and persistence behavior: establishes process-wide profiler state and global dashboard config state. It does not directly touch datastore or external services except through config installation side effects.

Dependencies and integration points: depends on `cloud.google.com/go/profiler`, `google.golang.org/appengine/v2`, syzkaller logging, and `mainConfig` supplied by environment-specific config files.

Risks: profiler startup failures are logged but non-fatal. Any panic from `installConfig` prevents the app from starting, which is correct for invalid static config. Tests generally use alternate entry points and `installConfig(testConfig)`, so this file has limited direct test coverage.

Test signals: no direct tests in this subset. Broad test setup indirectly validates `installConfig` behavior used by `main`.
