# sources/sync-backup/git-lfs/t/t-expired.sh

## Purpose

Validates Git LFS behavior when server-provided transfer actions are expired. It covers absolute, relative, and combined expiration forms for both HTTP batch actions and SSH authentication flows.

## Important APIs, control flow, and dependencies

The script loops over `absolute`, `relative`, and `both` expiration types. For each type it creates a specially named remote repository, tracks `*.dat`, commits `a.dat`, runs `GIT_TRACE=1 git push origin main`, and expects failure or an SSH-expiration trace. SSH cases set `lfs.url` to an `ssh://git@...` equivalent so `git-lfs-authenticate` is used.

## State, dependencies, integration points, risks, and test signals

State is limited to the generated commit, local object cache, remote object store, and server-side behavior keyed by repo name. Integration points are batch action expiration parsing, retry/failure handling, remote object write suppression, and SSH auth cache expiration. Risks include accepting expired upload URLs, persisting objects after failed pushes, or not refreshing expired SSH auth data. Signals are nonzero HTTP push status, `refute_server_object`, and `grep "ssh cache expired"` in push traces.
