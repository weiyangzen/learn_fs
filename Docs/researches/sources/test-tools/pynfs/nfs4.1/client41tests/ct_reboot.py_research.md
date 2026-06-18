# sources/test-tools/pynfs/nfs4.1/client41tests/ct_reboot.py

Purpose: NFSv4.1 client-side reboot/session/delegation behavior tests driven through local filesystem operations and a controllable test server environment.

Important APIs/types/functions: Imports `os` and `fail` from `.environment`. Public tests are `testReboot`, `testReboot2`, `testDelegReturn`, `testOpenZeroes`, `testSessionReset`, `testSessionReset2`, and `testTwoValueSetupOrCleanup`.

Control flow: Tests use `os.chdir`, local file/directory operations under `env.home`/`env.root`, and environment controls such as `reboot_server`, `set_error`, `set_error_wait_lease`, `clear_two_values`, `control_reset`, `control_record`, `control_pause`, `control_grab_calls`, `find_op`, and `set_two_values`. They simulate server reboot, delegation-return errors, bad session responses, and operation error injection.

State and persistence behavior: Creates/removes files and directories in the mounted NFS test area, changes process working directory, and mutates server-side error-injection configuration through environment helpers.

Dependencies and integration points: Depends on a special NFSv4.1 client test environment with action/config/control channels, plus constants such as `OP_OPEN` expected in the runtime namespace.

Risks: `testReboot2` references `data` in a failure message without defining it. `testDelegReturn` reuses `env.testname(t)` after reading, likely overwriting the same test file but the intent is recall-by-write. Global cwd mutation can affect later tests if failures interrupt cleanup.

Test signals: Uses `fail()` for mismatched file contents, directory listing, nonzero OPEN seqid/clientid, bad `--useparams`, and relies on absence of exceptions for reboot/session recovery paths.
