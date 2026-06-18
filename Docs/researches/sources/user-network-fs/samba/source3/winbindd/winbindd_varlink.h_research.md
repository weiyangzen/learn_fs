<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/winbindd/winbindd_varlink.h -->
# sources/user-network-fs/samba/source3/winbindd/winbindd_varlink.h

## Purpose
This header defines the varlink integration surface for winbindd's systemd userdb service.

## Important APIs, Types, And Functions
It declares `vl_active`, service/error string constants, the `WB_VL_ERR_CHECK_GOTO` error-handling macro, `wb_vl_fake_cli_state()`, user record functions, group record functions, membership functions, and `winbind_setup_varlink()`.

## Control Flow
The header has no runtime flow. Its macro standardizes local varlink error checks by logging `varlink_error_string(rc)` and jumping to a caller-supplied cleanup label.

## State And Persistence Behavior
It exposes the global recursion guard `vl_active`; all other state is owned by implementation files. No storage is persisted by the header itself.

## Dependencies And Integration Points
It includes talloc, tevent, and varlink headers, and is shared by `winbindd_varlink.c` plus the three method implementation files. It binds those files to the systemd userdb error namespace.

## Risks And Test Signals
Risks are ABI/API drift among the varlink files and the broad effect of the global `vl_active`. Compile coverage with and without `with_systemd_userdb` is the key signal, along with tests for every declared handler.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/winbindd/winbindd_varlink.h -->
