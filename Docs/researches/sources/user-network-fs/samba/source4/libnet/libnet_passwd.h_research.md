# sources/user-network-fs/samba/source4/libnet/libnet_passwd.h

## Purpose

`libnet_passwd.h` declares the libnet password operation contracts consumed by `libnet_passwd.c` and callers such as Python bindings and domain-join code. It models two families of operation: changing a password with old-password proof and setting a password with administrative authority.

## Important APIs, Types, and Functions

`enum libnet_ChangePassword_level` selects generic, SAMR, KRB5, LDAP, or RAP change-password backends. `union libnet_ChangePassword` defines shared `in` fields (`account_name`, `domain_name`, `oldpassword`, `newpassword`) and `out.error_string` for each backend view.

`enum libnet_SetPassword_level` selects generic, SAMR, SAMR-handle, concrete SAMR info levels 26/25/24/23/18, and placeholder KRB5/LDAP/RAP backends. `union libnet_SetPassword` defines generic and SAMR input (`account_name`, `domain_name`, `newpassword`) plus the SAMR-handle input containing `account_name`, `policy_handle *user_handle`, `dcerpc_pipe *dcerpc_pipe`, `newpassword`, and optional `samr_UserInfo21 *info21`.

## Control Flow

The header does not execute code, but its union layout allows dispatchers to treat `generic`, `samr`, and backend-specific arms as level-tagged views over common input/output structures. `samr_level` lets a generic or SAMR request force a concrete SAMR set-password level instead of trying the default sequence.

## State and Persistence Behavior

The structures are caller-owned request/response containers. They hold pointers to plaintext password strings and RPC handles but do not own external resources by themselves. Output persistence is limited to `error_string` allocations on the supplied talloc context in the implementation.

## Dependencies and Integration Points

The SAMR-handle arm depends on `struct policy_handle`, `struct dcerpc_pipe`, and `struct samr_UserInfo21` from Samba RPC headers included through libnet umbrella headers. `py_net.c`, `libnet_join.c`, and other management flows construct these unions before calling `libnet_SetPassword()` or `libnet_ChangePassword()`.

## Risks and Edge Cases

The union relies on the first fields matching across arms. Mis-setting `level` or `samr_level` can dispatch to the wrong backend or a not-implemented placeholder. The `rap` set-password arm declares `enum libnet_ChangePassword_level level`, which is unusual beside the other set-password arms and is worth caution if RAP support is ever implemented.

## Test Signals

Compile-time coverage catches structure drift. Runtime signals come from password-change/set tests using generic and SAMR-specific levels, especially forced concrete SAMR levels and SAMR-handle callers that pass or omit `info21`.
