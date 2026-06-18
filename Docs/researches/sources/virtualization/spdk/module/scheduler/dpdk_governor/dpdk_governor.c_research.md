# File Research: sources/virtualization/spdk/module/scheduler/dpdk_governor/dpdk_governor.c

Implements an SPDK governor backed by DPDK `rte_power`.

Key elements:
- Queries available and current core frequencies.
- Raises/lowers core frequency and sets min/max frequency.
- Reports core priority capabilities from DPDK power core capabilities.
- Dumps active DPDK power environment as JSON.
- Initializes by checking SMT coverage, selecting a supported DPDK power environment, initializing each core, and enabling turbo where supported.
- Deinitializes power management on all SPDK cores.
- Registers governor name `dpdk_governor`.

Dependencies:
- SPDK env/event/scheduler APIs and DPDK `rte_power` headers.

Research notes:
- Refuses initialization when the app core mask includes only part of an SMT sibling set.
- Handles DPDK header path differences around DPDK 24.11.
