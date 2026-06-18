# sources/user-network-fs/samba/source3/winbindd/winbindd_gpupdate.c

## Purpose
Schedules and runs Group Policy update commands from winbindd for machine policy and one-shot user policy application.

## Important APIs, Types, And Control Flow
`gpupdate_interval()` returns 90 minutes plus up to 30 minutes of random jitter. `gpupdate_init()` loads an S3 loadparm context, checks `lpcfg_apply_group_policies()`, and schedules an immediate timer. `gpupdate_callback()` invokes the configured `gpo update command` through `samba_runcmd_send()` with `--target=Computer` and `--machine-pass`, then schedules the next jittered timer. `gpupdate_user_init(user)` checks the same config and runs a user-targeted command immediately with `-U user`. `gpupdate_cmd_done()` logs nonzero command exit status.

## State And Persistence
Holds a talloc context and loadparm context for recurring machine timers. Actual policy persistence is performed by the external gpupdate command, not this file.

## Dependencies And Integration Points
Depends on global event context, loadparm, `samba_runcmd`, configured `gpo update command`, smb.conf path discovery, and winbind login/session paths that call user init.

## Risks And Test Signals
Risks include leaked contexts on early returns, missing NULL checks after `loadparm_init_s3()` in user path, external command failure visibility, and no recurring user timer despite the TODO. Test policy disabled, command missing/failing, custom smb.conf path, random interval bounds, machine timer rescheduling, and user invocation quoting.
