# sources/user-network-fs/samba/source3/script/tests/test_smbd_error.sh

## Purpose
This test verifies `smbd` behavior when a VFS `chdir` operation fails or panics. It confirms that an injected panic is logged as a panic and that a normal error such as `ESTALE` does not cause a panic.

## Important APIs, Functions, and Control Flow
The script loads `subunit.sh`, skips if `SMBD_DONT_LOG_STDOUT=1`, computes an `error_inject.conf` next to `SMB_CONF_PATH`, and counts `PANIC` lines in `$SMBD_TEST_LOG`. It writes `error_inject:chdir = panic` plus empty `panic action`, expects `smbclient //$SERVER_IP/error_inject -c dir` to fail, verifies the panic count increased by one, then writes `error_inject:chdir = ESTALE`, expects `smbclient` failure, and verifies no additional panic.

## State, Dependencies, Integration, and Risks
State is the injected config file and server log observation. It depends on the error-inject VFS module, live smbd log path, `SMBD_DONT_LOG_STDOUT`, and selftest reloading the config. Cleanup removes the config after each phase, but interruption can leave fault injection enabled. Test signals are exact panic count deltas and expected command failures.
