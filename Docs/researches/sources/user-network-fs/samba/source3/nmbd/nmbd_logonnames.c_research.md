# sources/user-network-fs/samba/source3/nmbd/nmbd_logonnames.c

## Purpose
Registers and tracks the domain logon server internet group name `WORKGROUP<1c>` when Samba is configured as a domain controller. Successful registration makes Samba advertise logon/domain-control capabilities.

## Important APIs, Types, And Functions
Public entry point is `add_logon_names()`. Internal helpers are `become_logon_server()`, `become_logon_server_success()`, and `become_logon_server_fail()`. It updates `work_record::log_state`, local server type bits, and uses `insert_permanent_name_into_unicast()` for `<1c>`.

## Control Flow
`add_logon_names()` iterates all subnets including unicast, finds `lp_workgroup()` with `LOGON_NONE`, skips if `<1c>` is already self-registered, and calls `become_logon_server()`. That sets `LOGON_WAIT` and registers `<1c>` as a group name. Success sets `LOGON_SRV`, marks server type as `SV_TYPE_NT | SV_TYPE_DOMAIN_MEMBER | SV_TYPE_DOMAIN_CTRL`, flags `work_changed`, and inserts a unicast mirror. Failure returns to `LOGON_NONE` and removes domain-controller type when possible.

## State And Persistence
State is held in `work->log_state`, server type bits, and namelist records for `WORKGROUP<1c>`. `subrec->work_changed` triggers browse/server-list persistence.

## Dependencies, Risks, And Test Signals
Called by `add_domain_names()` when `IS_DC` is true. Depends on name registration, workgroup/server helpers, LMB unicast insertion, and configuration. Risks include missing server records causing partial rollback and WINS/broadcast group-name differences. Test signals include `LOGON_WAIT` to `LOGON_SRV`, service bits, `<1c>` on broadcast/unicast namelists, and no duplicate registration.
