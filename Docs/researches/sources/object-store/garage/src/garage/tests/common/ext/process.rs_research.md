# sources/object-store/garage/src/garage/tests/common/ext/process.rs

Purpose: This file defines ergonomic assertion helpers for running Garage CLI commands from integration tests.

Important APIs and types: `CommandExt` is implemented for `std::process::Command`. It provides `quiet`, `expect_success_status`, and `expect_success_output`.

Control flow: `quiet` redirects stdout and stderr to null and returns the command for chaining. `expect_success_output` executes the command, panics if spawning fails, and if the exit status is nonzero panics with command debug data, status code, stdout, and stderr. `expect_success_status` delegates to `expect_success_output` and returns just the status.

State and persistence behavior: The helper itself has no persistent state but executes commands that mutate the integration Garage instance. It may suppress process output when `.quiet()` is used.

Dependencies and integration points: It is used by the test harness for setup and by tests that exercise CLI admin operations. It integrates process execution with assertion-style error reporting.

Risks: `quiet` can hide useful output unless `expect_success_output` is called without it. The helper panics on nonzero status, so tests cannot inspect expected failures through it. Commands are executed synchronously and can block if the invoked binary hangs.

Test signals: Harness startup and admin/bucket/website tests rely on this helper for layout assignment, key/bucket permissions, and website configuration.
