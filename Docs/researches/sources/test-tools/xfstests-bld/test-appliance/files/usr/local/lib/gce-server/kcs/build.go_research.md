# sources/test-tools/xfstests-bld/test-appliance/files/usr/local/lib/gce-server/kcs/build.go

Purpose: KCS kernel build handler and repository cache manager.

Important APIs/state: package globals `repoMap` and `repoLock` cache `*git.Repository` by parsed repo URL. `StartBuild` receives a `server.TaskRequest`, chooses a GCS kernel path, clones or reuses a repo, checks out the requested commit, builds/uploads the kernel, and optionally forwards a test request back to LTM.

Control flow: initialize KCS log dir in `init`; on request, set failure-report defers; read `GS_BUCKET`; derive repo id via `git.ParseURL`; lock all repo operations to serialize builds; call `git.NewRepository` on cache miss; call `repo.Checkout`; pass kernel config, build opts, and arch to `RunBuild` or `MockRunBuild`; update `GsKernel` and `ExtraOptions.Requester=KCSTest` before internal LTM dispatch.

State and dependencies: local repo cache under `/cache/repositories`, KCS build logs in `/var/log/go/kcs_logs`, GCS kernel object `kernels/bzImage-<testID>-onerun.deb`, and SendGrid failure mail. Depends on `util/git`, `util/gcp`, `util/server`, and external build upload script through `RunBuild`.

Risks and test signals: `repoLock` serializes all repo builds, reducing race risk but limiting concurrency. `repoMap` is in-memory and stale repo directories may outlive processes. Mock mode tests result forwarding, while real validation requires a configured KCS host.
