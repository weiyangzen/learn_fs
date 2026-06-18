# sources/user-network-fs/rclone/bin/markdown-lint

Purpose: local wrapper around the same markdownlint globs defined in `.github/workflows/build.yml`. It extracts globs from the `Check Markdown format` workflow step with `awk` and runs `davidanson/markdownlint-cli2` in Docker with the repository mounted at `/workdir`.

State changes are limited to Docker image pulls/cache and container execution. Dependencies are Docker, workflow file structure, `awk`, and a working current directory at repo root. Risks include brittle YAML parsing with awk, unquoted `$PWD` and globs, Docker user mapping issues, and mismatch if workflow structure changes. Test signal is markdownlint exit status.
