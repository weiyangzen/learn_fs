# File Research: sources/virtualization/nvme-cli/libnvme/src/nvme/private.h

## Role

Central internal libnvme header. It defines Linux ioctl command shims, fabrics configuration, controller creation parameters, transport-handle state, topology object internals, stats state, global context state, private helpers, logging, and internal function prototypes.

## Key Content

- Declares sysfs path accessors:
  - `libnvme_subsys_sysfs_dir()`
  - `libnvme_ctrl_sysfs_dir()`
  - `libnvme_ns_sysfs_dir()`
  - `libnvme_slots_sysfs_dir()`
  - `libnvme_uuid_ibm_filename()`
  - `libnvme_dmi_entries_dir()`
- Defines Linux passthrough ioctl command layouts:
  - `struct linux_passthru_cmd32`
  - `struct linux_passthru_cmd64`
- Defines ioctl constants for reset, rescan, admin/io passthrough, and io_uring commands.
- Defines fabrics tuning:
  - `struct libnvme_fabrics_config`
  - `struct libnvme_ctrl_params`
  - `libnvme_fabrics_config_copy()`
- Defines transport handle state:
  - `enum libnvme_transport_handle_type`
  - `enum ioctl_state`
  - `enum libnvme_io_uring_state`
  - `struct libnvme_transport_handle`
- Defines topology and stats internals:
  - `struct libnvme_stat`
  - `struct libnvme_path`
  - `struct libnvme_ns_head`
  - `struct libnvme_ns`
  - `struct libnvme_ctrl`
  - `struct libnvme_subsystem`
  - `struct libnvme_host`
  - `struct libnvme_global_ctx`
- Defines fabrics option presence flags in `struct libnvme_fabric_options`.
- Declares JSON config/tree functions and core open/create/lookup functions.
- Declares fabrics and hostname/address helpers:
  - `traddr_is_hostname()`
  - `hostname2traddr()`
  - `libnvmf_default_config()`
  - `libnvmf_read_sysfs_fabrics_attrs()`
- Declares logging with `__libnvme_msg()` and `libnvme_msg()`.
- Provides small utilities:
  - `xstrdup()`
  - `streq0()`
  - `streqcase0()`
  - `round_up()`
- Declares key import, network address matching, key-value parsing, namespace transport handle management, MI admin passthrough, and io_uring open/close helpers.

## Dependencies

- Includes system stat/string headers, conditional `ifaddrs.h`, CCAN lists, internal/public NVMe type headers, and `nvme/tree.h`.
- Exposes conditional fields for `CONFIG_LIBURING`, `CONFIG_MI`, and `CONFIG_FABRICS`.
- Uses code-generation annotations for accessors and Python binding aliases.

## Research Notes

This file is the internal schema for libnvme's object graph. The public tree API is backed by these structs, but many fields are guarded by generated accessors or custom read/write annotations. The double-buffered stats in namespaces and paths are explicitly documented: `stat[curr_idx]` is current, `stat[!curr_idx]` is previous, and `diffstat` decides raw versus delta reporting.

## Filesystem/Storage Relevance

The file models how NVMe controllers, namespaces, paths, and hosts are represented in user space. It bridges sysfs topology, ioctl passthrough, io_uring passthrough, and fabrics configuration for storage tooling.
