# Research: sources/user-network-fs/gcsfuse/tools/integration_tests/emulator_tests/configs/config.yaml

Purpose: minimal proxy-server configuration for emulator tests that need a pass-through target to the storage testbench JSON endpoint.
Important keys: `targetHost: http://localhost:9000`, matching the storage-testbench HTTP endpoint started by `emulator_tests.sh`.
Control flow: no executable logic; the proxy server consumes this YAML to route requests to the emulator without injected retry, stall, or validation behavior.
State and persistence: holds endpoint configuration only. Persistent test state remains in the storage testbench bucket and mounted files.
Dependencies and integration points: used by proxy-server tooling under `tools/integration_tests/proxy_server` and by tests/util helpers that launch the proxy with `--config-path`.
Risks and edge cases: assumes the emulator is listening on localhost port 9000 and that tests run with host networking. Port mismatch causes proxy startup or request failures.
Test signals: success is indirect: proxy starts, logs listening port/PID, and storage clients using `STORAGE_EMULATOR_HOST` reach the emulator.
