<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/winbindd/winbindd_varlink.c -->
# sources/user-network-fs/samba/source3/winbindd/winbindd_varlink.c

## Purpose
This file exposes winbindd through systemd's `io.systemd.UserDatabase` varlink interface. It sets up the service socket, validates the requested service name, dispatches user/group/membership calls to async helper files, and prevents recursive varlink calls back into itself.

## Important APIs, Types, And Functions
The public setup entry point is `winbind_setup_varlink()`. `wb_vl_fake_cli_state()` builds a minimal `winbindd_cli_state` from varlink peer credentials. The method handlers are `io_systemd_getuserrecord()`, `io_systemd_getgrouprecord()`, and `io_systemd_getmemberships()`. `vl_active` is a global recursion guard.

## Control Flow
Setup creates `/run/systemd/userdb` or configured socket directory, builds a `unix:` URI using the configured service name, creates a varlink service, registers the interface and handlers, obtains the service fd, and adds it to tevent. Method handlers parse `service` plus optional name/id parameters, reject wrong services with `BadService`, reject recursive calls when `vl_active` is set, set `vl_active`, and dispatch to the relevant `wb_vl_*` async function. The tevent fd handler calls `varlink_service_process_events()`.

## State And Persistence Behavior
Persistent process state is the `wb_vl_state` talloc object holding the varlink service, event context, fd event, and fd. The global `vl_active` flag is reset by per-call state destructors. Filesystem persistence is limited to creating the socket directory and varlink socket managed by the varlink service.

## Dependencies And Integration Points
It depends on libvarlink, tevent, talloc, Samba config parameters under `winbind varlink`, peer credential retrieval through `SO_PEERCRED`, and the helper functions declared in `winbindd_varlink.h`. It integrates with systemd-userdb clients and internal winbind request handlers by synthesizing fake client state.

## Risks And Test Signals
Risks include global `vl_active` serializing or rejecting overlapping varlink requests, Linux-specific peer credential behavior, service-name mismatches, socket lifecycle errors, and incorrect error mapping where dispatch failures become `ServiceNotAvailable`. Test signals are varlink socket creation, `BadService` handling, recursion prevention, peer credential capture, and all dispatch quadrants for user/group/membership calls.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/winbindd/winbindd_varlink.c -->
