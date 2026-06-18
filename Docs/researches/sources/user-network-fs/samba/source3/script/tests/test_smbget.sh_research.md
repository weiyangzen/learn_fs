# sources/user-network-fs/samba/source3/script/tests/test_smbget.sh

## Purpose
This Bash blackbox suite validates `smbget` download modes: guest access, explicit credentials, UPN/domain formats, credentials in SMB URLs and auth files, interactive password prompting, recursive downloads including empty directories, resume/update behavior, MSDFS paths, rate limiting, encryption, Kerberos ccache, and trusted-domain Kerberos.

## Important APIs, Functions, and Control Flow
The script accepts server/IP/domain/realm credentials, domain user credentials, workdir, and `SMBGET`. It loads `subunit.sh` and `common_test_fns.inc`, resolves `kinit` through `system_or_builddir_binary`, and uses `texpect` for interactive password entry. `create_test_data` writes random files and directories in `$WORKDIR`; each `test_*` clears the download area, invokes `$SMBGET` with a specific auth or transfer mode, and validates exit status plus `cmp` against source files. Kerberos tests create `KRB5CCNAME=FILE:$TMPDIR/smget_krb5ccache` and call `kerberos_kinit`.

## State, Dependencies, Integration, and Risks
State is local random test data in `$WORKDIR`, downloads in `$SELFTEST_TMPDIR`, temporary auth/expect files, empty directories, and Kerberos ccache files. Integration points include `smbget_guest`, `smbget`, `msdfs-share`, KDC, trust environment variables, and `texpect`. Risks include time-sensitive rate limiting using wall-clock seconds, residual files on failure, and environment-only trust variables. Test signals are exit codes, byte comparisons, directory-existence checks, and expected failure status for modified resume.
