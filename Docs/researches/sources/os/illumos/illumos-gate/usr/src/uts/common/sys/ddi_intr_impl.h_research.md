# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ddi_intr_impl.h

This is the private implementation header for the DDI interrupt framework. It defines interrupt bus operation opcodes, handle internals, soft interrupt internals, MSI-X state, interrupt resource management pools and requests, per-devinfo interrupt state, private helper prototypes, and legacy intrspec support.

`ddi_intr_op_t` enumerates nexus interrupt operations: supported types, interrupt counts, allocation/free, priority get/set, ISR add/remove, duplicate vector, enable/disable, block enable/disable, capability get/set, mask/unmask, pending query, available count, resource pool access, and target get/set.

`ddi_intr_handle_impl_t` is the in-core representation of a `ddi_intr_handle_t`. It records dip, interrupt type, inum, vector, version, state, capabilities, priority, per-handle rwlock, callback function/args, MSI-X duplication flags and main handle pointer, platform-private data, scratch fields used by framework/nexus handoff, and a target processor snapshot.

The internal state flags track allocated, handler-added, and enabled states. Validation macros check interrupt type and allocation behavior. MSI-X allocation constants set default/min/max allocation behavior. `ddi_intr_msix_t` stores MSI-X table and PBA access handles, addresses, offsets, and device access attributes.

Interrupt Resource Management is represented by `ddi_irm_pool_t`, `ddi_irm_req_t`, and `ddi_irm_params_t`. Pools track interrupt vector supply, policy, requested/reserved counts, locks, condition variables, balancing thread, owner dip, and request lists. Requests attach a device to a pool with type, requested/available counts, scratch state, and list linkage.

`devinfo_intr_t` is the per-device interrupt cache used from `struct dev_info`. It stores supported types, MSI-X data, current type/count/enabled count, legacy handle array, x86 PCI config handle/capability pointer, and optional IRM request.

The bottom section preserves `struct intrspec` for old DDI interrupt interfaces and declares obsolete intrspec operations. It also declares affinity helpers, `i_ddi_intr_ops`, softint helpers, devinfo interrupt init/fini, state getters/setters, IRM operations, handle lookup, MSI-X getter/setter, x86 PCI config helper accessors, interrupt weight accessors, and platform handle allocation/free.

Research notes:
- This file is private and tightly coupled to `devops.h` bus operation revisioning.
- `NEXUS_HAS_INTR_OP()` requires busops revision at least 9 and a `bus_intr_op`.
- IRM introduces asynchronous balancing/threading state; pool locks and flags are important for correctness.
- Legacy intrspec APIs coexist for old driver compatibility but are explicitly obsolete.
