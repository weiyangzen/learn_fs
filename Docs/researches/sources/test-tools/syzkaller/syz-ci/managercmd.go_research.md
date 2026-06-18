# sources/test-tools/syzkaller/syz-ci/managercmd.go

Purpose: supervises a single `syz-manager` subprocess.

Important APIs/types/functions: `ManagerCmd`, `Errorf`, `NewManagerCmd`, `Close`, and `ManagerCmd.loop`.

Control flow: constructor starts a goroutine. The loop starts the process no more often than every ten minutes, rotates log/bench files, redirects stdout/stderr to the manager log, observes process exit, restarts unexpected exits, and on `Close` sends SIGINT then kills after one minute if needed.

State and persistence: writes manager log and bench files, rotating previous versions to `.old`.

Dependencies and integration points: used by `Manager.restartManager`; depends on `osutil.Command`, `osutil.Rename`, and Unix signals.

Risks: restart throttling means a crashed manager may stay down until period expires. Close is synchronous and assumes loop can respond. Uses SIGINT, so non-Unix portability is limited.

Test signals: no direct tests in this subset.
