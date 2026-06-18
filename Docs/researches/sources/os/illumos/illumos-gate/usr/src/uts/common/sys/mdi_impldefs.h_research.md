# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/mdi_impldefs.h

Purpose: Defines internal Multiplexed Device Interface (MDI/MPxIO) structures, locks, state flags, pathinfo state transitions, vhci cache data, path selection, and failover APIs.

Architecture described:
- `mpxio` provides the core multipath framework.
- vHCI drivers manage a multipath class, such as `scsi_vhci`.
- pHCI drivers provide physical transport paths.
- Client devices are target/leaf drivers such as disk drivers.
- `mdi_pathinfo` nodes connect client devices and pHCIs into a matrix.

Key structures:
- `mdi_vhci_ops_t`: vHCI callbacks for path init/uninit/state change, failover, client attach, and support probing.
- `mdi_vhci_t`: registered virtual HCI with class name, devinfo, config, load-balancing policy, pHCI list, and client hash.
- `mdi_phci_t`: physical HCI with path list, flags, unstable counter, and vHCI-private data.
- `mdi_client_t`: multipath client with GUID, driver name, load-balancing policy, path list, state, failover/power/unconfigure state, and private data.
- `struct mdi_pathinfo`: per path tuple tying client to pHCI with address, instance, state, properties, private data, kstats, preferred flag, and flags.
- `mdi_pi_kstats` and `pi_errs`: per client-pHCI aggregate I/O/error stats.
- `mdi_vhci_cache_t`, `mdi_vhci_config_t`, and related cache structs: on-disk vHCI busconfig cache and asynchronous path configuration state.

State and locking:
- The header documents lock granularity and ordering across global MDI, vHCI pHCI/client locks, pHCI lock, client lock, and pathinfo lock.
- pHCI/client unstable counters block hotplug/failover during transient path state.
- pHCI and client flags cover offline, suspend, power down, detach, user/driver disable, transient disable, and power transition.
- Pathinfo macros implement init, online, offline, standby, fault, transient, hidden, removed, and disable states while preserving extended-state bits.

Key APIs:
- vHCI registration: `mdi_vhci_register()`, `mdi_vhci_unregister()`.
- Path counts and path-to-devinfo helpers for pHCI/client.
- Path selection: `mdi_select_path()`, load-balancing setters/getter, selection flags.
- Failover: `mdi_failover()` with sync/async flags.
- Device support probe: `mdi_is_dev_supported()`.
- Path kstat helpers and path state/private-data helpers.
- Property packing and obsolete path iteration helpers.

Relevance to subset A: Highly relevant storage infrastructure. This is the main block-storage/multipathing contract in the group and directly affects disk path selection, failover, hotplug behavior, and observability.
