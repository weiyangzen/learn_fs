# sources/user-network-fs/samba/source3/script/tests/test_smbspool.sh

## Purpose
This test validates printing through `smbspool`, `smbspool_krb5_wrapper`, device URI handling, argv0 sanitization, virtual printer queue verification, and delete-on-close behavior.

## Important APIs, Functions, and Control Flow
The script accepts server/IP/credentials/target env, loads `subunit.sh` and `common_test_fns.inc`, and resolves `vlp`, `smbspool`, `smbspool_argv_wrapper`, `smbtorture3`, and `smbspool_krb5_wrapper`. Helper `test_smbspool_noargs` checks discovery output. `test_smbspool_authinforequired_none/unknown` cover wrapper environment behavior. `test_vlp_verify` inspects `$PREFIX/$TARGET_ENV/lockdir/vlp.tdb` using `vlp lpq`, validates a job id and spool file, then removes the job. `test_delete_on_close` runs `smbtorture3 DELETE-PRINT` and confirms the queue size does not change.

## State, Dependencies, Integration, and Risks
State includes the `vlp.tdb` virtual print queue and spool files under the target environment. It depends on printing testdata `example.ps`, `vlp` output fields, environment variables `DEVICE_URI` and `AUTH_INFO_REQUIRED`, and printer shares `print1`/`print4`. Risks include queue residue if verification/removal fails and field-position parsing with `awk`. Test signals combine command exit statuses, queue validation, job file existence, and queue count stability.
