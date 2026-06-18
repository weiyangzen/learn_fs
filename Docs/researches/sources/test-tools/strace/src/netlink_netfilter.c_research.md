<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/netlink_netfilter.c -->
# sources/test-tools/strace/src/netlink_netfilter.c

Purpose: decodes `NETLINK_NETFILTER` payload headers and generic netfilter attributes.

Important APIs/types/functions: `decode_netlink_netfilter`, `struct nfgenmsg`, `netfilter_versions`, and netfilter subsystem/type xlats.

Control flow: skips `NLMSG_DONE`, prints `nfgen_family`, `version`, and `res_id` from `nfgenmsg`; then decodes trailing attributes unless the message is a batch control or reserved type, in which case it prints raw hex. It includes workarounds for historical nftables `res_id` endianness.

State and persistence behavior: no durable state; per-payload only.

Dependencies and integration points: invoked by main netlink dispatcher for `NETLINK_NETFILTER`; uses `nlattr`, `<linux/netfilter/nfnetlink.h>`, and network byte-order helpers.

Risks: netfilter subsystems have many nested formats that are not decoded here beyond generic attributes. The `res_id` workaround is protocol-specific and must remain accurate for nftables.

Test signals: cover nfgenmsg printing, batch begin/end, nftables res_id endian variants, short payloads, raw reserved payloads, and generic trailing attributes.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/netlink_netfilter.c -->
