# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/clients/of/sol_ofs/sol_kverb_impl.h

This private Solaris OFS kernel-verbs header defines event-firing macros, OFED-to-IBTF conversion macros, and OFS client state.

Core definitions:
- `FIRE_QP_EVENT` and `FIRE_CQ_EVENT` acquire the OFS client reader lock, check that the object and event handler exist and the device is open, fill `ib_event`, call the OFED event handler, then release the lock.
- Conversion macros map OFED page size, QP state, static rate, path migration state, and path MTU values to IBTF forms.
- `gfp_t` is typedefed for OFED compatibility.
- `ofs_client_t` maps an OFED `ib_client_t` to IBTF module/client handles, HCA counts, device/client lists, a lock, and initialization state.

Risk-sensitive invariants:
- Async events are discarded when the device registration state is `IB_DEV_CLOSE`.
- Event callbacks run while the client lock is held as reader, so callback behavior must avoid deadlocking with client teardown.
- Conversion macros assume enum compatibility between OFED-visible and IBTF-visible values.
