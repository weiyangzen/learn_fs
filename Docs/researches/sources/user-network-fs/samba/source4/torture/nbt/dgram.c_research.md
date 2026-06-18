
# sources/user-network-fs/samba/source4/torture/nbt/dgram.c

## Purpose
`dgram.c` defines NetBIOS datagram torture tests for UDP/138 mailslot-based NETLOGON and NTLOGON behavior. It sends primary-domain-controller and SAM logon discovery requests to a resolved domain/workgroup name, waits for datagram replies, parses them as netlogon responses, and checks response type, command, version flags, user echoing, PDC name format, and account-control behavior.

## Important APIs, Types, And Functions
`netlogon_handler()` is a `dgram_mailslot_handler` callback that allocates `struct nbt_netlogon_response` storage and parses incoming datagrams via `dgram_mailslot_netlogon_parse_response()`. `nbt_test_netlogon()` sends a `LOGON_PRIMARY_QUERY` to `NBT_MAILSLOT_NETLOGON` and expects `NETLOGON_GET_PDC`. `nbt_test_netlogon2()` sends multiple `LOGON_SAM_LOGON_REQUEST` variants, joins a temporary machine account with `torture_join_domain()`, and verifies responses for unknown and trusted workstation cases. `nbt_test_ntlogon()` performs similar checks using `NBT_MAILSLOT_NTLOGON`. `torture_nbt_dgram()` registers the `dgram` suite with `netlogon`, `netlogon2`, and `ntlogon` tests.

## Control Flow
Each test creates an NBT datagram socket, resolves the configured workgroup/domain logon name with `resolve_name_ex()`, chooses a local interface IP via `iface_list_best_ip()`, then tries to bind the datagram socket to the configured datagram port. If binding the low port fails, it falls back to an ephemeral port, with comments noting this may prevent replies from some Windows versions. Tests create temporary mailslot listeners, build `struct nbt_netlogon_packet` requests, send with `dgram_mailslot_netlogon_send()`, and run the tevent loop until a reply arrives or five seconds elapse. More advanced paths join and leave a temporary domain machine account and repeat requests with SID and account-control fields.

## State And Persistence
Socket, mailslot, and response state are talloc-owned and per-test. `dgmslot->private_data` is used as both callback output and loop condition. Persistent external state occurs when `nbt_test_netlogon2()` and `nbt_test_ntlogon()` create a temporary workstation trust account named `TORTURE_TEST`; cleanup is done with `torture_leave_domain()`. The tests also rely on transient UDP network state and local port binding permissions.

## Dependencies
Dependencies include `libdgram`, socket abstractions, tevent, name resolution, network interface discovery, loadparm ports/workgroup, torture RPC join helpers, generated NBT/netlogon structures, and NBT mailslot constants. The target environment must have a reachable domain controller or Samba server responding to NBT logon datagrams.

## Integration Points
The suite is added by `torture_nbt_init()` in `nbt.c`. It validates Samba's datagram server behavior and compatibility with Windows netlogon conventions. Temporary domain joins integrate with Samba's RPC/LDAP account-management test helpers, while name resolution integrates with configured resolver policy.

## Risks
The low-port fallback changes test observability: inability to bind UDP/138 can make some valid servers appear silent. The timeout loops reuse a `struct timeval tv` initialized near the start of the test; in multi-step tests this can shorten later waits if not reset around each send. Temporary domain joins can leave accounts behind if a fatal assertion exits before cleanup. The callback replaces `private_data` with newly allocated response storage and returns silently on allocation failure, which appears as a timeout. Tests are environment-sensitive and may fail under firewalls, wrong interface selection, or missing NBT service.

## Test Signals
Positive signals are received datagram replies, parsed `NETLOGON_GET_PDC` or `NETLOGON_SAMLOGON` response types, correct command constants, expected NT version flag combinations, correct user-name echoing, and expected UNC/non-UNC PDC name formatting. Negative signals include assertion failures on send, parse, timeout, account join, or response field mismatches.
