# sources/user-network-fs/gcsfuse/tools/package_gcsfuse/main.go

Purpose: CLI entry point for building release packages from a version and optional commit.

Important APIs/types/functions: `run(args []string)` and `main`.

Control flow: validates `dst_dir version [commit]`, defaults commit to `v<version>`, checks required tools, builds the release tree, and on Linux emits both deb and rpm packages.

State/persistence behavior: writes package artifacts to the destination directory and deletes the temporary build directory after packaging.

Dependencies/integration: dispatches to platform-specific `checkForTools`, `build`, `packageDeb`, and `packageRpm`.

Risks/test signals: only Linux packaging is implemented; non-Linux runs can build but do not package. The rpm error is wrapped as `packageDeb`, a copy/paste message issue.
