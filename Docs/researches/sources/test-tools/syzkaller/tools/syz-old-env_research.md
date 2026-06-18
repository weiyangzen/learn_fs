# sources/test-tools/syzkaller/tools/syz-old-env

## Purpose
`syz-old-env` is a Bash wrapper for running syzkaller development commands inside the older `gcr.io/syzkaller/old-env` Docker image, or a locally built equivalent when `SYZ_ENV_BUILD` is set.

## Important APIs, types, and functions
- It builds `COMMAND`, `BUILDARGS`, and `DOCKERARGS` from proxy environment variables, command arguments, CI mode, rootless Docker detection, and `SOURCEDIR=...` rewrites.
- `SCRIPT_DIR` locates the syzkaller checkout relative to the script.
- It selects image `old-env` when invoked as `syz-old-env`, otherwise `env`, sharing implementation with the newer wrapper naming.

## Control flow
The script translates each CLI argument into a container command. `SOURCEDIR=/path` is special-cased into a bind mount at `/syzkaller/kernel` plus a rewritten command argument. Non-CI runs add `-it`. It then builds or pulls the image and runs Docker with syzkaller source, cache, Docker socket, Go env, CI/GitHub env, and user mapping.

## State and persistence behavior
It can pull or build Docker images, mount the host syzkaller tree read/write, mount `$HOME/.cache`, mount the Docker socket, and run commands that create files as the host user when possible. It does not persist wrapper-local state.

## Dependencies and integration points
Requires Docker, the syzkaller Docker image definitions under `tools/docker`, and host permissions for Docker. It is intended to wrap Make targets such as format, presubmit, and extract.

## Risks and edge cases
The `[ -n $http_proxy ]` style tests are unquoted and can misbehave for unset or whitespace-containing values. Array-like expansions use variables initialized as strings, relying on Bash behavior. Passing the Docker socket into the container is powerful and should be treated as host-level access. Rootless detection controls file ownership behavior.

## Test signals
No automated tests. Manual validation should cover rootless and rootful Docker, CI vs interactive mode, proxy propagation, `SOURCEDIR` mounting, and local image build mode.
