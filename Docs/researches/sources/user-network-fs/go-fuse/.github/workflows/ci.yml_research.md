# sources/user-network-fs/go-fuse/.github/workflows/ci.yml

Purpose: GitHub Actions CI definition for go-fuse. It runs on push, pull request, and a daily scheduled job at 12:00 UTC.

Important configuration: matrix tests Go versions 1.21.x through 1.26.x and `GOMAXPROCS` values default/all CPUs and `1`, with `fail-fast: false`. Steps install Go, check out full history for `git describe`, install `fuse3`, `libssl-dev`, and `libfuse-dev`, enable `user_allow_other`, then run `./all.bash`.

Control flow/state: CI is stateless per job but relies on Ubuntu runner kernel/FUSE support and root via sudo for selected tests.

Dependencies/integration: integrates with `all.bash`, package tests, benchmark compilation, and root-required FUSE paths. Risks include future Go-version availability, Ubuntu package changes, and scheduled failures from kernel/libfuse behavior. Test signal is the complete matrix across versions and single-CPU mode, which is important for deadlock/race exposure.
