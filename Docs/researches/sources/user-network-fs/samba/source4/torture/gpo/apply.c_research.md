# sources/user-network-fs/samba/source4/torture/gpo/apply.c

## Purpose
This file implements the `gpo.apply.gpo_param_from_gpo` torture test. It verifies that Samba's GPO update command applies, skips reapplying, force reapplies, and unapplies domain password policy settings from SYSVOL `GptTmpl.inf` into SAMDB domain attributes.

## Important APIs, Types, and Functions
`gpo_apply_suite()` creates the `apply` suite and registers `torture_gpo_system_access_policies()`. `exec_wait()` runs the configured GPO update command asynchronously via `samba_runcmd_send()`, polls with `tevent_req_poll_ntstatus()`, and returns the child exit status from `samba_runcmd_recv()`. `unix2nttime()` converts negative AD interval strings to days for comparing `minPwdAge` and `maxPwdAge`.

Constants `GPODIR`, `GPOFILE`, `GPTTMPL`, and `GPTINI` define the SYSVOL policy paths and generated security template. The tested SAMDB attributes are `minPwdAge`, `maxPwdAge`, `minPwdLength`, and `pwdProperties`.

## Control Flow
The test resolves the configured `sysvol` path, creates the default domain policy SecEdit directory, fetches `gpo update command`, connects to SAMDB as `system_session()`, and stores the original domain password-policy attributes. It then iterates three policy vectors, writes `GptTmpl.inf`, increments `GPT.INI` version, runs the update command, searches SAMDB, and asserts that all four attributes match the vector.

After the apply loop, the test resets SAMDB attributes to the original message using `LDB_FLAG_MOD_REPLACE`, runs the normal update command again, and asserts the settings are not reapplied without a version/force trigger. It builds a command with `--force`, verifies the last vector is reapplied, then builds a command with `--unapply` and verifies original SAMDB values are restored.

## State and Persistence Behavior
This is an integration test with real side effects. It creates and overwrites files under SYSVOL for the default domain policy, increments `GPT.INI`, invokes the configured GPO updater process, and modifies domain password-policy attributes in SAMDB. It attempts to restore the original SAMDB attributes through unapply, but file contents and GPT version changes remain part of the test environment. It relies on talloc cleanup for local allocations, not on transaction rollback.

## Dependencies and Integration Points
The file depends on loadparm for SYSVOL path and GPO command, `mkdir_p()`, SAMDB connection helpers, system session credentials, LDB search/modify APIs, the tevent command runner, and the smbtorture assertion framework. It integrates into `TORTURE_GPO` through `gpo_apply_suite()` and `torture_gpo_init()`.

## Risks
Running this test against a non-disposable domain can alter password policy and SYSVOL contents. It assumes the AD DNS name/path `addom.samba.example.com` and default domain policy GUID layout, so environments with different names or layouts may fail unless provisioned for this test. Command construction appends `--force` and `--unapply` to the configured command array, so unusual wrapper commands may not accept those flags. If the test aborts before reset/unapply, policy settings can be left changed.

## Test Signals
Passing signals include successful command execution, SAMDB search returning exactly one base object, applied attribute values matching each generated template, normal re-run preserving manually restored values, `--force` reapplying the latest template, and `--unapply` restoring original values.
