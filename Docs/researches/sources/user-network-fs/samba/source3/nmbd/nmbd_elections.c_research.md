# sources/user-network-fs/samba/source3/nmbd/nmbd_elections.c

## Purpose
Implements NetBIOS browser election behavior for local master browser selection. It checks for an existing master, initiates elections, sends election mailslot datagrams, compares criteria, and promotes or demotes Samba based on results.

## Important APIs, Types, And Functions
Public functions are `check_master_browser_exists()`, `run_elections()`, `process_election()`, `check_elections()`, and `nmbd_message_election()`. Internal helpers are `send_election_dgram()`, `check_for_master_browser_success()`, `check_for_master_browser_fail()`, and `win_election()`. It uses `work_record` election fields and global `StartupTime`.

## Control Flow
`check_master_browser_exists()` periodically queries `WORKGROUP<1d>` where Samba is not LMB; failure forces or stimulates an election. `check_elections()` starts pending elections only after local `WORKGROUP<1e>` registration. `run_elections()` sends election datagrams every two seconds and declares a win after four uncontested sends, then calls `become_local_master_browser()`. `process_election()` parses incoming elections, ignores foreign workgroups, compares version/criterion/uptime/server name, starts a local election if Samba outranks the sender, or demotes if Samba loses while participating/master.

## State And Persistence
Election state is in-memory on `work_record`: `RunningElection`, `needelection`, `ElectionCount`, `ElectionCriterion`, and `mst_state`. Promotion/demotion effects are delegated to LMB code and name registration/release layers.

## Dependencies, Risks, And Test Signals
Depends on query/mailslot infrastructure, `WORKGROUP<1e>` registration, and LMB promotion/demotion APIs. Risks include incorrect election comparison order, sending before `<1e>` registration, and time-gated behavior. Test signals include forced election messages, high/low criterion packets, demotion after losing, no packets before `<1e>`, and promotion after four cycles.
