# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/iterator/iter_priv.c

`iter_priv.c` implements iterator filtering for configured private addresses and private domains. `priv_create()` allocates a regional allocator plus an address tree for blocked netblocks and a name tree for domains allowed to contain those private addresses.

`priv_apply_cfg()` clears the regional allocator, reloads `private-address` entries with `netblockstrtoaddr()`, reloads `private-domain` names with `sldns_str2wire_dname()`, and initializes parent pointers for efficient lookup. Duplicate address/domain entries are ignored with verbose logging.

The main enforcement path is `priv_rrset_bad()`. Public-name A and AAAA RRsets are scanned for configured private addresses; bad individual RRs are removed when possible via `msgparse_rrset_remove_rr()`, and the whole RRset is removed when all RRs are gone. Owner names under configured private domains are exempt.

The file also handles SVCB/HTTPS privacy filtering by parsing `ipv4hint` and `ipv6hint` svcparams from the RDATA. Hints containing private addresses are treated the same as A/AAAA private-address leakage. Malformed SVCB/HTTPS data is generally tolerated unless a private address can be found inside the remaining bytes.

This subsystem is used by iterator scrubbing to prevent public DNS answers from returning RFC1918/private or otherwise configured internal addresses unless the name is explicitly whitelisted as private.
