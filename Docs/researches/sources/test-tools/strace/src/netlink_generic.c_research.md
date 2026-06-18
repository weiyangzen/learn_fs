<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/netlink_generic.c -->
# sources/test-tools/strace/src/netlink_generic.c

Purpose: generic netlink payload dispatcher that prints `genlmsghdr` and routes known generic families to specialized decoders.

Important APIs/types/functions: `decode_netlink_generic`, default `decode_genl_msg`, `genl_decoders`, `initialize_genl_decoders`, and `lookup_genl_decoder`.

Control flow: after rejecting too-short or `NLMSG_DONE` payloads, it fetches `struct genlmsghdr`, lazily resolves configured family names to dynamic ids via `genl_families_xlat`, selects a decoder by `nlmsg_type`, and falls back to printing generic attributes.

State and persistence behavior: process-local static initialization caches dynamic generic family ids, currently for `nlctrl`.

Dependencies and integration points: integrates with `netlink_generic.h`, `nlattr.h`, `genl_families_xlat`, and the main netlink dispatcher for `NETLINK_GENERIC`.

Risks: generic family ids are dynamic; stale or unavailable family xlat data causes fallback decoding. Only families listed in `genl_decoders` receive semantic attribute decoding.

Test signals: generic netlink tests should include known `nlctrl`, unknown family ids, short headers, reserved fields, attributes after `genlmsghdr`, and id initialization under multiple tracees.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/netlink_generic.c -->
