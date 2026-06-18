# sources/user-network-fs/samba/source3/nmbd/nmbd_become_dmb.c

## Purpose
Implements the state machine for becoming a NetBIOS Domain Master Browser (DMB) for the configured workgroup. DMB ownership is represented by the `WORKGROUP<1b>` name. The file coordinates WINS-first registration when Samba is a WINS client and broadcast registration when it is not, then updates workgroup/server state so browser synchronization can use the new DMB role.

## Important APIs, Types, And Functions
The code operates on `struct subnet_record`, `struct work_record`, `struct server_record`, `struct nmb_name`, and asynchronous `struct response_record` callbacks from the name-query and registration layers. Public entry point `add_domain_names(time_t t)` periodically adds domain logon names and DMB names. Internal stages include `become_domain_master_browser_wins()`, `become_domain_master_browser_bcast()`, `become_domain_master_query_success()`, `become_domain_master_query_fail()`, `become_domain_master_stage1()`, `become_domain_master_stage2()`, and `become_domain_master_fail()`.

## Control Flow
`add_domain_names()` is timer-gated by `CHECK_TIME_ADD_DOM_NAMES`. If Samba is a domain controller it first calls `add_logon_names()`. If `lp_domain_master()` is true, it either queries/registers `WORKGROUP<1b>` through WINS on `unicast_subnet`, or broadcasts per local subnet. Query success is normally a conflict, but responses containing one of Samba's own IPs, all-ones broadcast, or zero are tolerated for compatibility with old Samba behavior and continue to stage 1. Query failure is expected unless a unicast WINS query returns an error other than `NAM_ERR`. Stage 1 sets `work->dom_state = DOMAIN_WAIT` and calls `register_name()` for `<1b>`. Stage 2 marks `DOMAIN_MST`, adds `SV_TYPE_NT | SV_TYPE_DOMAIN_MASTER`, flags `subrec->work_changed`, and either cascades WINS success to broadcast subnets or inserts the broadcast DMB name into `unicast_subnet`.

## State And Persistence
Primary mutable state is in `work->dom_state`, the local server record's service type bits, `work->dmb_name`, `work->dmb_addr`, and `subrec->work_changed`. Registration success also creates or updates `SELF_NAME` and `PERMANENT_NAME` records through `register_name()` and `insert_permanent_name_into_unicast()`. The namelist writer is signaled by `work_changed`; WINS/unicast name data ultimately persists in nmbd's namelist/WINS storage layers.

## Dependencies, Risks, And Test Signals
Integrates with `nmbd_nameregister.c`, `nmbd_namequery.c`, `nmbd_become_lmb.c`, `nmbd_logonnames.c`, and browser sync code. Risks include asynchronous rollback gaps, first-interface IP selection for WINS DMB identity, and compatibility hacks masking conflicts. Test signals include simulated WINS/broadcast `<1b>` conflicts, `DOMAIN_MST` transitions, service type bit changes, and namelist/debug output for `WORKGROUP<1b>`.
