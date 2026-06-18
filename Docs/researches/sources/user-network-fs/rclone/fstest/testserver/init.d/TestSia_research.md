
# sources/user-network-fs/rclone/fstest/testserver/init.d/TestSia

Purpose: starts a Sia antfarm test network for rclone Sia backend integration.

Important APIs/types/functions: `wait_for_sia` polls `/renter/uploadready` for `"ready":true`. `start` pulls `ivandeex/sia-antfarm:latest`, maps API to `127.0.0.1:39980`, waits up to 300 seconds, and emits `type=sia` with `api_url`.

Control flow: Docker pull, run, readiness polling through exported shell function, config echo. `stop` captures container logs to `sia-test.log` before killing.

State/persistence: disposable container; local log file `sia-test.log` accumulates stop logs.

Dependencies/integration: Docker, curl, timeout, Sia backend tests.

Risks: pulling `latest` makes runs network-dependent and non-reproducible. Startup can take minutes. Local log file can grow over repeated runs.

Test signals: upload-ready API response and successful Sia operations.
