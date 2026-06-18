# sources/test-tools/strace/bundled/linux/include/uapi/linux/mroute.h

Purpose: defines IPv4 multicast routing socket option/ioctl ABI, virtual interface and multicast forwarding cache structures, PIM control messages, and rtnetlink multicast route attributes.

Important APIs/types/functions: exports `MRT_*` commands, `SIOCGETVIFCNT`, `SIOCGETSGCNT`, `SIOCGETRPF`, flush flags, `vifbitmap_t`, `vifi_t`, VIF bitmap macros, `vifctl`, `mfcctl`, `sioc_sg_req`, `sioc_vif_req`, `igmpmsg`, `IPMRA_*` attributes, and `IGMPMSG_*` pseudo-message types.

Control flow: multicast routing daemons enable MRT, add/delete VIFs and MFC entries, receive cache-miss/register messages on raw sockets, query counters, set PIM/assert/table behavior, and flush caches/interfaces.

State/persistence behavior: commands mutate per-netns multicast routing tables, VIFs, cache entries, counters, and daemon mode until `MRT_DONE` or namespace teardown. Counter queries are observational.

Dependencies/integration: includes sockios, Linux types, and IPv4 address definitions. Integrates with IGMP/PIM daemons, rtnetlink table dumps, and raw IP sockets.

Risks and test signals: legacy BSD-compatible structs and bitmaps are ABI-sensitive. Tests should cover all `MRT_*` options, flush flags, VIF flags, flexible control messages, counter ioctls, and netlink nested VIF/cache-report attrs.
