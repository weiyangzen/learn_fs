# sources/user-network-fs/gcsfuse/tools/package_gcsfuse/build.go

Purpose: builds a gcsfuse release tree from a requested git commit/tag and version for packaging.

Important APIs/types/functions: `build(commit, version)`.

Control flow: creates temp GOCACHE, output, and git clone directories; clones `GoogleCloudPlatform/gcsfuse` at the commit; builds `tools/build_gcsfuse`; runs it with source dir, output dir, and version; then renames `bin` to `usr/bin` for Linux package layout.

State/persistence behavior: creates temp directories and returns a build output directory that caller later deletes. Network clone and local build outputs are key side effects.

Dependencies/integration: used by `package_gcsfuse/main.go`; requires `git`, `go`, and reachable GitHub repository.

Risks/test signals: cloning from a fixed remote makes builds network-dependent. Error cleanup removes output only when returning an error; successful cleanup is caller-owned.
