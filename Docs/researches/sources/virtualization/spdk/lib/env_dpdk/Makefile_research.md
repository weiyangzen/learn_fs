# File Research: sources/virtualization/spdk/lib/env_dpdk/Makefile

Builds the SPDK `env_dpdk` library with ABI version `17.0`. It compiles core environment, memory, PCI, initialization, threading, DPDK PCI compatibility, PCI event, SIGBUS, and device-specific PCI helper sources, including both DPDK 22.07 and 22.11 compatibility translation units.

The makefile also generates `spdk_dpdklibs` pkg-config files from the deduplicated DPDK library list, rewrites the env_dpdk pkg-config `Requires:` line to depend on `spdk_dpdklibs`, and provides install/uninstall targets for the generated DPDK dependency pkg-config file.
