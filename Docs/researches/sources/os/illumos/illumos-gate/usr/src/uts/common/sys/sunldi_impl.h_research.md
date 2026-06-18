# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/sunldi_impl.h

`sunldi_impl.h` is the private implementation header for LDI. It defines hash sizes for handles and idents, keeps obsolete event support enabled behind `LDI_OBSOLETE_EVENT`, declares handle flags, and exposes `ldi_init()`.

Private STREAMS link helpers bridge LDI handles/files into STREAMS mux linking (`ldi_mlink_lh`, `ldi_mlink_fp`, `ldi_munlink_fp`). `struct ldi_ident` records hash linkage, refcount, module name/id, major number, devinfo pointer, and dev_t. `struct ldi_handle` records hash linkage, refcount, flags, handle type, identity pointer, vnode pointer, and obsolete-event state protected by `lh_lock`.

Obsolete `ldi_event_t` stores per-handle callback linkage and handler information. The newer callback implementation `ldi_ev_callback_impl_t` records handle, devinfo, dev_t/spec type, notify/finalize function pointers, callback argument, cookie/id, and list linkage. `struct ldi_ev_callback_list` documents a careful locking and in-progress-walk protocol: unregistering callbacks during notify/finalize walks is supported by walker-next/walker-prev fields.

Internal event delivery functions invoke notify/finalize callbacks and bridge DDI offline notifications. The device usage interface defines `ldi_usage_t`, which reports source module/name/devinfo/dev_t and target module/name/devinfo/dev_t/spec type. `ldi_usage_count()` and `ldi_usage_walker()` allow devinfo/fuser-style consumers to enumerate kernel device clients without knowing LDI internals.
