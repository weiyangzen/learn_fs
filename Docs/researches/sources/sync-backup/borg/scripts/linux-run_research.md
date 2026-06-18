# sources/sync-backup/borg/scripts/linux-run

Purpose: Runs commands inside a Linux Podman container for Borg development/testing, with FUSE support and a selectable Python base image.

Important APIs/types/functions: Bash function `usage()` prints help. Config variables are `BASE_IMAGE`, `IMAGE_NAME`, and `CONTAINER_NAME`. Parsed options are `--image IMAGE`, `--rebuild`, `--help`, and `--` to stop option parsing. Uses an array `COMMAND` and constructs a `podman run` command.

Control flow: `set -euo pipefail` fail-fast. Parses options until a command is encountered, verifies `podman`, tags image name by replacing `:` in base image, builds `scripts/Dockerfile.linux-run` when requested or missing, then runs an interactive container executing the given command or `/bin/bash`.

State and persistence: Builds/updates a local Podman image `borg-test-env:<tag>`, creates transient `borg-test-runner` containers, mounts the repository at `/app`, and uses a Podman volume for `/tmp`.

Dependencies and integration points: Requires Podman, the Dockerfile, current working directory being the Borg repo, FUSE device availability, and host permissions for `--cap-add SYS_ADMIN` and `/dev/fuse`. Integrates with tox commands and FUSE test environments.

Risks: The help message references Homebrew on all platforms, which may be misleading. Fixed container name conflicts if another run is active. Privileged/FUSE flags are necessary but increase container capability surface.

Test signals: Run `scripts/linux-run --image python:3.11 tox -e py311-none`, run a FUSE-capable env if host supports it, test `--rebuild`, and verify mounted workspace writes are owned correctly with `--userns=keep-id`.
