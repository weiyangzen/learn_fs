# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/adapters/hermon/hermon_cmd.h

## Purpose
Defines the firmware command interface for the Hermon HCA: opcodes, status values, mailbox management structures, outstanding command tracking, command-post arguments, MAD helper constants, endian-swap helpers, and command posting prototypes.

## Main Interfaces
- Firmware command opcodes cover init/close/query, TPT/MPT/MTT, EQ, CQ, QP transitions, special QPs, SRQ, multicast, diagnostics, ICM mapping, FCoIB, health check, and interrupt moderation.
- Command status constants include PRM statuses plus driver-local timeout/resource/invalid-status values.
- `hermon_mbox_t`, `hermon_mboxlist_t`, `hermon_mbox_info_t`: mailbox pool and allocation descriptors.
- `hermon_cmd_t`, `hermon_cmdlist_t`: outstanding command slots and completion synchronization.
- `hermon_cmd_post_t`: generic firmware command post payload matching HCR fields.
- MAD helper macros and endian conversion macros for PortInfo, NodeInfo, GUIDInfo, and PKeyTable responses.

## Dependencies And Relationships
Includes `sys/ib/mgt/sm_attr.h` for SM MAD structures. Depends heavily on hardware structures from `hermon_hw.h` and resource/handle typedefs from the wider Hermon driver. The public prototypes are used throughout initialization, QP/CQ/MR/EQ transitions, multicast management, FCoIB setup, and diagnostics.

## Research Notes
The command path supports both polling and event-completion models through `HERMON_CMD_SLEEP_NOSPIN` and `HERMON_CMD_NOSLEEP_SPIN`. Lock annotations describe mailbox and command-list ownership and lock ordering.
