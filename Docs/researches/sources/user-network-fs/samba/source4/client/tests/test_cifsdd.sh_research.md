# sources/user-network-fs/samba/source4/client/tests/test_cifsdd.sh

## Purpose
Blackbox test script for `cifsdd`, validating that the utility can copy data through local and SMB-backed inputs/outputs without content changes.

## Important APIs, types, and functions
- Sources `testprogs/blackbox/subunit.sh` for `testit` reporting.
- `runcopy()` invokes `$BINDIR/cifsdd` with Samba config, debug level, domain, username, and password.
- `compare()` wraps `cmp` under subunit.

## Control flow
The script requires `SERVER USERNAME PASSWORD DOMAIN`. It creates a temporary source file in `$SELFTEST_TMPDIR` using `dd if=$DD` with 50 KiB of data, then loops over block sizes `512`, `4k`, and `48k`. For each block size it tests local-to-local, local-to-remote then remote-to-local, and remote-to-remote then remote-to-local, comparing the final destination with the source after each scenario.

## State and persistence behavior
Creates local temp files named with `$$` under `SELFTEST_TMPDIR` and remote files in the `tmp` share. It removes local temp files at the end but does not explicitly delete the remote temp files.

## Dependencies and integration points
Depends on a working Samba selftest environment, `$BINDIR/cifsdd`, `$CONFIGURATION`, optional `$VALGRIND`, credentials accepted by `//$SERVER/tmp`, and `/bin/dd`/`cmp`.

## Risks and edge cases
- Remote files are not cleaned up, which can leave state behind across failures or repeated runs.
- The source data comes from the `cifsdd` binary, not random or sparse data.
- It does not test direct I/O, sync I/O, invalid UNC paths, short writes, EOF corner cases, or permission failures.

## Test signals
Strong signal for normal copy integrity across local and SMB I/O paths at three block sizes. It is especially relevant to `cifsddio.c` buffer and path backend behavior.
