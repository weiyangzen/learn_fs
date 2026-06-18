# sources/test-tools/syzkaller/dashboard/app/local_ui_test.go

Purpose: developer fixture and optional local HTTP server for exploring a populated dashboard UI.

Important APIs/types/functions: flags `-local-ui`, `-local-ui-addr`, `-local-ui-user`; `TestLocalUI`; `localUIConfig`; `populateBuildsAndCrashes`; `populateLocalUIDB`; `tickRandom`.

Control flow: test creates a Spanner-capable context, installs local config, populates rich data, and exits unless `-local-ui` is set. In serving mode it listens, serves static files, wraps real HTTP requests as App Engine test requests, injects optional login, and delegates to the app mux.

State/persistence: creates builds, crashes, reports, fixed bugs, manual repro tasks, AI jobs, AI trajectory spans, lore-like external reports, comments, and patch iterations in the test datastore/Spanner context.

Dependencies/integration: touches app config, aetest auth, HTTP mux, reporting, crash/build upload, manual repro APIs, AI workflow APIs, trajectory logging, external report APIs, Spanner context, and Linux target metadata.

Risks/test signals: serving mode is intentionally long-running and requires `-timeout=0 -v`; random trajectory data varies; failures can originate across many subsystems. Automated signal is successful fixture population; main value is manual UI inspection.
