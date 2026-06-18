# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ddi_hp_impl.h

Private DDI hotplug implementation header. It defines sync/async request flags, registered connection handles, async event entries, bus hotplug operation commands, connector/port dispatch macros, sysevent subclasses, list helpers, and internal helper prototypes.

Key elements:
- Request flags distinguish synchronous and asynchronous hotplug requests.
- `DDI_HP_IS_VIRTUAL_PORT()` tests whether a connection handle represents a virtual port.
- `ddi_hp_cn_handle_t` links a devinfo node to its `ddi_hp_cn_info_t` and to the next registered connector/port.
- `ddi_hp_cn_async_event_entry_t` stores async event target dip, connection name, and requested target state.
- `ddi_hp_op_t` enumerates bus hotplug operations: get/change state, probe/unprobe, get/set property, create port, and remove port.
- `DDIHP_CN_OPS()` dispatches operations to port or connector handlers based on connection type.
- `NEXUS_HAS_HP_OP()` checks whether a nexus driver has a bus ops vector new enough to provide `bus_hp_op`.
- Sysevent subclasses distinguish state-change events and hotplug requests.
- `DDIHP_LIST_APPEND` and `DDIHP_LIST_REMOVE` manipulate simple singly linked handle lists.
- Declares internal functions for modctl entry, connection-name lookup, state retrieval, port/connector ops, sysevent generation, and connection unregister.

Dependencies:
- Depends on public `ddi_hp.h`, DDI devinfo internals through `DEVI()`, bus ops revisions, and sysevent infrastructure.
- Used only in kernel hotplug implementation code.

Research notes:
- Dispatch splits virtual-port behavior from physical connector behavior while presenting a shared operation enum.
- The list macros are unguarded by locking; callers must provide synchronization around connection handle lists.
