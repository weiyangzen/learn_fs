# sources/user-network-fs/samba/source3/lib/netapi/examples/join/netdomjoin.c

## sources/user-network-fs/samba/source3/lib/netapi/examples/join/netdomjoin.c

Purpose: Demonstrates online domain join through `NetJoinDomain()`.

Important APIs/types/functions: Accepts host, domain, account OU, account, password, and join flags; defaults flags to `NETSETUP_JOIN_DOMAIN | NETSETUP_ACCT_CREATE`.

Control flow: Initializes context, parses options/positionals, calls `NetJoinDomain()`, prints context error string on failure or success notice, and frees resources.

State and persistence behavior: Mutates local/remote machine join state and domain computer account state depending on flags.

Dependencies and integration points: Online counterpart to offline join samples and GUI join workflow.

Risks: Requires privileged credentials and may require reboot. Incorrect flags can create or reuse computer accounts unexpectedly.

Test signals: Join a disposable test host or container to a test domain, verify with `getjoininformation`, then unjoin through other tools.
