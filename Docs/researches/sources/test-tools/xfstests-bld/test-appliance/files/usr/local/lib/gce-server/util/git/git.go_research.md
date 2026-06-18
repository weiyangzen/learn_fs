# sources/test-tools/xfstests-bld/test-appliance/files/usr/local/lib/gce-server/util/git/git.go

Purpose: repository management for KCS builds/bisects and LTM branch watchers.

Important types/APIs: `Repository` tracks local repo id/url/base/dir with a mutex; `RemoteRepository` tracks remote URL/branch/head. APIs include `NewRepository`, `GetCommit`, `Checkout`, `Valid`, `BisectStart`, `BisectStep`, `BisectLog`, `BisectReset`, `BuildUpload`, `Delete`, `Dir`, `NewRemoteRepository`, `Update`, `Head`, `getHead`, and `ParseURL`.

Control flow: `NewRepository` ensures `/cache/repositories/linux.reference` mirror exists, derives a base repo directory from URL, clones with reference if needed, then clones a shared per-id working repo and fetches all remotes. `Checkout` first tries direct hex commit checkout, then fetches and tries `origin/<commit>` and `<commit>`. Bisect methods wrap Git CLI commands and classify test results into `good`, `bad`, or `skip`. `BuildUpload` invokes `/usr/local/lib/gce-build-upload-kernel` with build/GCS env. Remote watcher uses `git ls-remote --heads`.

State and dependencies: persistent repo cache under `/cache/repositories`, Git CLI, reference Linux mirror, build upload shell script, and locks per repository.

Risks and test signals: shared clone/cache layout depends on marker cleanup scripts and Git object availability. `ParseURL` assumes at least two path elements and no SSH scp-style URLs. Tests are environment-gated to KCS for clone/checkout and likely expensive; parser tests for URL edge cases would be useful.
