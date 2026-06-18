# sources/user-network-fs/samba/source3/winbindd/winbindd_ping_dc.c

## sources/user-network-fs/samba/source3/winbindd/winbindd_ping_dc.c

`winbindd_ping_dc.c` implements asynchronous `WINBINDD_PING_DC`, returning whether a domain controller can be contacted and, when available, the contacted DC name. State stores `dcname` and the child operation result.

`winbindd_ping_dc_send()` selects the target domain: blank domain preserves old behavior by using `find_our_domain()`, otherwise it uses `find_trust_from_name_noinit()`. Unknown domains return `NO_SUCH_DOMAIN`. Internal passdb-based domains are considered always contactable and synthesize the DC name from `lp_netbios_name()` plus `lp_dnsdomain()` when present, lowercasing the host component. Non-internal domains send `dcerpc_wbint_PingDc_send()` to the domain child.

The callback receives both transport and child operation status with `dcerpc_wbint_PingDc_recv()` and stores `state->result`; transport/operation errors are propagated via tevent. `winbindd_ping_dc_recv()` sets auth error fields if `state->result` is non-OK, copies `dcname` into `extra_data`, updates response length, and returns OK for successfully completed command processing.

There is no local persistence, but the child may initialize or test domain connections and current DC state. Dependencies include generated wbint stubs, domain lookup helpers, loadparm NetBIOS/DNS settings, talloc string helpers, and `set_auth_errors()`. Risks include inconsistent semantics where command transport success can return OK while auth fields contain a DC ping result, NULL `lp_dnsdomain()` handling, synthesized internal DC names, and stale domain online state. Test signals include blank-domain ping, trusted-domain ping, unknown domain, internal domain with/without DNS domain, child failure setting auth errors, and returned cstring length.
