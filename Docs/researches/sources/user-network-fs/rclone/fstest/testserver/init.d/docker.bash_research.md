
# sources/user-network-fs/rclone/fstest/testserver/init.d/docker.bash

Purpose: shared Docker lifecycle helpers for testserver init scripts.

Important APIs/types/functions: `stop` stops container `$NAME` if `status` says it is running. `status` checks `docker ps --format '{{.Names}}'` for an exact name. `docker_ip` extracts the first Docker network IP via `docker inspect`.

Control flow: helper functions are sourced by concrete scripts and invoked by `run.bash` dispatch.

State/persistence: no direct persistent state; acts on Docker containers named by callers.

Dependencies/integration: Docker CLI and caller-defined `NAME`.

Risks: exact-name grep must be correctly quoted by callers; Docker network IPs may not be reachable on all host configurations. No force removal here; `run.bash force-stop` calls script-level `stop`.

Test signals: `status` exit code and successful Docker stop/IP lookup.
