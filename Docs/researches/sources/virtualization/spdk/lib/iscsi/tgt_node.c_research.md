# File Research: sources/virtualization/spdk/lib/iscsi/tgt_node.c

Full-file read: 1422 lines.

This file implements iSCSI target-node core behavior: access control, SendTargets output, portal/initiator mapping, target construction/destruction, redirection, LUN mutation, CHAP settings, histogram allocation, and JSON serialization.

Main responsibilities:
- Match IPv4/IPv6 initiator addresses against initiator-group netmasks, including `ANY`.
- Enforce initiator IQN allow/deny rules, including `!` deny entries.
- Generate discovery `TargetName` and `TargetAddress` text responses with continuation support via `conn->send_tgt_completed_size`.
- Maintain target-to-portal-group and portal-group-to-initiator-group maps with manual refcounts.
- Construct SPDK SCSI devices and add SCSI ports/LUNs.
- Safely destruct targets after requesting connection logout and waiting for active connections to drain.
- Configure public-portal redirection to private portal destinations.
- Emit target info/config JSON and optional histogram-enable config.
- Allocate/free target latency histograms.

Important control flow:
- `iscsi_tgt_node_access` checks the connection portal group, target mapping, initiator name, and initiator address before allowing login.
- `iscsi_send_tgts` walks all targets under `g_iscsi.mutex`, filters by target name and initiator visibility, and writes as much as fits.
- Mapping add/remove functions roll back prior changes on failure.
- `iscsi_tgt_node_destruct` marks the target destructed, requests logout, then either polls active connection count or destructs the SCSI device immediately.
- `iscsi_tgt_node_construct` validates CHAP, maps short names through `g_iscsi.nodebase`, validates IQN-ish formatting, constructs the SCSI dev, adds maps, sets auth/digest/queue-depth, and registers globally.

Integration points:
- Depends on portal groups, initiator groups, connection state, SPDK SCSI devices/LUNs/ports, and histogram APIs.
- RPC handlers call most public mutation APIs here.
- Login/discovery code depends on access checks, redirect checks, and SendTargets construction.

Risks and review notes:
- IPv4/IPv6 CIDR parsing rejects prefix length 0, so `/0` is not accepted; `ANY` is the intended universal match.
- `iscsi_tgt_node_delete_ig_maps` ignores missing-map errors, suitable for global cleanup but important to understand.
- `iscsi_tgt_node_add_lun` refuses LUN changes while active connections exist.
- Redirection validates numeric host/port and requires redirect target not be in the same public group, but the private-group requirement is enforced indirectly by “different private portal group” policy checks.
- Target JSON includes CHAP flags and group id but not redirect settings.

Testing focus:
- Access matrix across allow/deny IQNs, IPv4/IPv6 netmasks, `ANY`, and portal mappings.
- SendTargets continuation with small buffers.
- Map add/remove rollback.
- Target destruction while connections are active.
- Redirect configure/clear validation.
