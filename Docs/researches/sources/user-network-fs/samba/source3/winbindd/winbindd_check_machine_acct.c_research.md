# sources/user-network-fs/samba/source3/winbindd/winbindd_check_machine_acct.c

## Purpose

`winbindd_check_machine_acct.c` implements the async parent-side handler for `WINBINDD_CHECK_MACHINE_ACCT`. It resolves a domain and delegates machine-account validation to that domain's winbind child.

## Important APIs, Types, and Functions

- `struct winbindd_check_machine_acct_state` is an empty tevent state holder.
- `winbindd_check_machine_acct_send()` selects the target domain and starts `dcerpc_wbint_CheckMachineAccount_send()`.
- `winbindd_check_machine_acct_done()` receives transport and operation results.
- `winbindd_check_machine_acct_recv()` returns status and populates auth error fields with `set_auth_errors()`.

## Control Flow

If no domain name is supplied, the handler preserves compatibility by using `find_our_domain()`. Otherwise it uses `find_domain_from_name()`. Missing domains fail with `NT_STATUS_NO_SUCH_DOMAIN`; internal domains complete immediately because they are passdb-based and assumed contactable. External domains are checked through `dom_child_handle(domain)`, and the callback errors if either RPC or child result fails.

## State and Persistence Behavior

The file owns no persistent state. It only manages tevent request state and writes authentication error information into the winbind response on receive.

## Dependencies and Integration Points

It depends on winbind request dispatch, domain lookup, domain child RPC handles, tevent, generated winbind RPC stubs, and response auth-error helpers. Actual validation happens in the child implementation.

## Risks and Edge Cases

Empty domain fallback must be preserved. Internal domains always pass here, so this does not validate passdb health. Error handling must merge transport and child result status.

## Test Signals

Test empty-domain fallback, missing domain, internal-domain success, child success/failure, transport failure, and `set_auth_errors()` output on receive.
