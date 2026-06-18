# sources/user-network-fs/samba/source3/nmbd/nmbd_become_lmb.c

## Purpose
Implements local master browser promotion and demotion for a workgroup on a broadcast subnet. LMB ownership is represented by `__MSBROWSE__<01>` and `WORKGROUP<1d>`. The file also maintains unicast-subnet aliases so directed queries for local-master names still resolve in broadcast-only configurations.

## Important APIs, Types, And Functions
Public APIs are `become_local_master_browser()`, `unbecome_local_master_browser()`, `insert_permanent_name_into_unicast()`, and `set_workgroup_local_master_browser_name()`. Important callbacks include `become_local_master_stage1()`, `become_local_master_stage2()`, `become_local_master_fail1()`, `become_local_master_fail2()`, `unbecome_local_master_success()`, and `unbecome_local_master_fail()`. It manipulates `work_record::mst_state`, `ElectionCriterion`, `local_master_browser_name`, server type bits, and `name_record` entries.

## Control Flow
Promotion starts only with `lp_local_master()` enabled and `AM_POTENTIAL_MASTER_BROWSER(work)`. `become_local_master_browser()` sets `MST_BACKUP`, raises election bits, and registers `__MSBROWSE__<01>`. Stage 1 sets `MST_MSB`, mirrors MSBROWSE to unicast, then registers `WORKGROUP<1d>`. Stage 2 marks `MST_BROWSER`, switches server type from potential to master browser, sets the local master name, asks servers to announce if the list is small, mirrors `<1d>` to unicast, and resets announce timing. Demotion releases `<1d>` and MSBROWSE, immediately processes response records, then resets state and may force an election.

## State And Persistence
The file updates workgroup state, election flags, server service bits, and namelist entries. `insert_permanent_name_into_unicast()` uses the IP list of a unicast `PERMANENT_NAME` as a reference count across broadcast subnets. `subrec->work_changed` signals browse-list persistence.

## Dependencies, Risks, And Test Signals
Depends on `register_name()`, `release_name()`, workgroup/server database helpers, and namelist helpers. It is called from election wins, duplicate-master conflict handling, reset handling, and shutdown paths. Risks include stale callback userdata, unicast IP reference-count errors, and demotion/election races. Test signals include election-to-LMB transition logs, `__MSBROWSE__<01>`/`WORKGROUP<1d>` namelist presence, service bit changes, and release cleanup after failures.
