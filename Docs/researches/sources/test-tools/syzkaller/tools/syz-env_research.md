# sources/test-tools/syzkaller/tools/syz-env

Purpose: `syz-env` runs syzkaller development commands inside the official syzkaller Docker environment image or a locally built equivalent.

Important APIs and flow: it collects proxy settings into Docker build/run args, rewrites `SOURCEDIR=<path>` arguments into a mounted `/syzkaller/kernel`, defaults to interactive `-it` outside CI, picks `env` or `old-env` image based on executable basename, uses rootless Docker detection to decide whether to pass `--user`, pulls `gcr.io/syzkaller/<image>` unless `SYZ_ENV_BUILD` is set, and finally runs Docker with syzkaller source, cache, Docker socket, GOPATH, CI/GitHub/Fuzzit environment variables, and the requested command via `-c`.

State and persistence: uses host source checkout, `$HOME/.cache`, and Docker image cache. Local build mode creates/updates `syz-env` or `syz-old-env` images.

Dependencies and integration: requires Docker, optional local Dockerfile under `tools/docker/<image>`, and host project layout. It is intended to wrap `make` and extraction commands.

Risks: `[ -n $http_proxy ]` style unquoted tests can behave unexpectedly for empty or whitespace-containing values. Mounting Docker socket gives container broad host Docker control. Command construction is string-based and can be sensitive to shell quoting.

Test signals: no automated test. Manual signal is successful container pull/build and command execution with correct file ownership.
