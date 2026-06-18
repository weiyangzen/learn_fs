# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/mac_flow.h

## Role

Public flow descriptor and resource-control types for MAC packet classification, bandwidth/CPU/ring assignment, priority, and protection settings.

## Structure

Defines flow selector mask bits, `flow_desc_t`, maximum rings and flow name lengths, CPU/fanout/resource structures, transmit interrupt CPU state, priority levels, protection flags and data structures, resource property mask bits/defaults/minimums, `mac_resource_props_t`, field alias macros, and `MAC_COPY_CPUS()`.

## Dependencies And Consumers

Includes types, param, IP protocol definitions, and Ethernet definitions. Used by MAC client APIs, flow management, dladm/dld plumbing, and internal classifier/resource code.

## Important Details

`flow_desc_t` is packed to 4-byte alignment on mixed 64/32-bit long-long alignment platforms, preserving ABI layout. `MRP_MAXBW_RESETVAL` disables bandwidth control, and `MRP_MAXBW_MINVAL` rejects sub-megabit limits below current implementation capability.

## Research Notes

Read completely: 266 lines, 7835 bytes.
