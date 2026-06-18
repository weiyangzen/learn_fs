# sources/test-tools/strace/src/rtnl_nsid.c

Purpose: Decodes network namespace ID route-netlink messages.

Important APIs/types/functions: nsid route decoder and attr table for namespace id/fd/target ids.

Control flow: prints family or minimal fixed message context, then delegates attrs to scalar/fd decoders.

State and persistence: stateless.

Dependencies/integration: netlink route dispatcher, Linux rtnetlink namespace attrs, fd and s32 decoders.

Risks: small file with mostly table-driven behavior; future attrs need table updates.

Test signals: RTM_GETNSID/NEWNSID messages with fd, nsid, target nsid, and malformed attrs.
