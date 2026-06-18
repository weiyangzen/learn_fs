# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/pcmcia.h

## Purpose
Defines private PCMCIA nexus, adapter-driver, card-services, socket/window, device-node, resource, property, and regspec interfaces.

## Main Interfaces
- Capacity constants for adapters, sockets, windows, and power entries.
- Nexus names and node type strings:
  - `PCMCIA_NEXUS_NAME`
  - `PCMCIA_ADAPTER_NODE`
  - `PCMCIA_SOCKET_NODE`
  - `PCMCIA_PCCARD_NODE`
- Adapter/Card Services ops:
  - `pcmcia_if_t`
  - `pcmcia_cs_t`
  - call-through macros such as `GET_ADAPTER`, `GET_SOCKET`, `SET_WINDOW`, `SET_IRQ`, `CLEAR_IRQ`.
- Nexus private state:
  - `pcmcia_adapter_nexus_private`
  - `pcm_regs`
  - `inthandler_t`
  - `pcmcia_parent_private`
  - `pcmcia_adapter`
  - `pcmcia_logical_window_t`
  - `pcmcia_mif`
- Socket/resource helpers:
  - `socket_enum_t`
  - `PR_GET`, `PR_SET`, `PR_CLEAR`, `PR_ZERO`
  - `PR_MAX_IO_LEN`, `PR_MAX_MEM_LEN`, range/count constants.
- Device matching and node construction:
  - `pcm_device_info`
  - `pcm_dev_node_t`
  - `init_dev_t`
  - `str_int_t`
  - device class, function, manufacturer, VERSION_1, JEDEC, naming, and no-CIS flags.
- 1275-style regspec helpers:
  - `PC_REG_*`
  - `PC_GET_REG_*`
  - `PC_INCR_REFCNT`
  - `PC_DECR_REFCNT`
  - `PC_REG_PHYS_HI`
- Property identifiers such as `PCMCIA_PROP_SOCKET`, `PCMCIA_PROP_REG`, and `PCMCIA_PROP_INTR`.

## Dependencies And Relationships
Includes `sys/modctl.h` and uses DDI types, `dev_info_t`, `dev_ops`, interrupt cookies, soft interrupts, kernel mutexes, and Card Services concepts. It is the common contract between the PCMCIA nexus, adapter-specific drivers, and card services.

## Research Notes
This is a broad private compatibility header. Several macros encode 1275-compatible `reg` properties and also carry Solaris-private reference counts in the same physical-high word.
