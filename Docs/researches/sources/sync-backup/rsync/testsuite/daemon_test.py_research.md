# sources/sync-backup/rsync/testsuite/daemon_test.py

Purpose: basic daemon-mode listing and path coverage through both remote-shell daemon syntax and the test daemon transport.

Important APIs/types/functions: `fleet_nonroot`, `listed_paths`, `build_rsyncd_conf`, `start_test_daemon`, `run_and_check`, `run_rsync('-VV')`, `rsync_argv`, `RSYNC_PEER`, and support `lsh.sh --no-cd`.

Control flow: create source paths under `foo` and `bar`, ensure `rsyncd.conf` symlink, add `--config` when running as root, verify module listing through lsh and daemon includes expected modules and not `test-hidden`, recursively list hidden module by explicit name and compare exact path set, list `test-from/f*` glob and compare exact path set, and repeat glob listing with `-U` if atime support exists.

State and persistence behavior: no full copy is required; exact listing sets are the assertions. Hidden module remains usable by name while absent from module listing.

Dependencies and integration points: daemon module list generation, hidden module handling, glob expansion, remote-shell daemon invocation, optional atime listing format, fleet nonroot pass.

Risks and test signals: parser extracts last listing token and assumes no spaces in paths. Failures indicate listing leaks/omissions or glob path resolution regressions.
