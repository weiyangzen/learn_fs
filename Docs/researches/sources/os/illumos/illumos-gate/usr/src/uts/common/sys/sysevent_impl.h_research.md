# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/sysevent_impl.h

## Purpose
Defines the private sysevent implementation ABI: packed event buffer layout, attribute packing helpers, syseventd door upcall structures, channel/subscriber internals, kernel private entry points, event-channel ioctl payloads, and `/dev/sysevent` constants.

## Main Interfaces
- Packed event representation:
  - `se_name_t`
  - `se_value_t`
  - `sysevent_attr_impl_t`
  - `sysevent_hdr_t`
  - `sysevent_impl_t`
- Event access and layout macros:
  - `SYSEVENT_IMPL()`, `SE_VERSION()`, `SE_CLASS_NAME()`, `SE_SUBCLASS_NAME()`, `SE_PUB_NAME()`
  - `SE_ALIGN()`, `SE_SIZE()`, `SE_ATTR_OFF()`
  - `SYS_EVENT_VERSION`, `SE_PACKED_BUF`
- Door/upcall queue structures:
  - `log_event_upcall_arg_t`
  - `log_eventq_t`
  - `LOGEVENT_DOOR_UPCALL`
- Registration/channel structures:
  - `subclass_lst_t`
  - `class_lst_t`
  - `se_pubsub_t`
  - `sysevent_channel_descriptor_t`
- Kernel-private log APIs: `log_event_init()`, `log_sysevent_flushq()`, `log_usr_sysevent()`, copyout/free/register helpers, and ID generation.
- Event channel internals:
  - queue/list primitives `evch_dlelem_t`, `evch_dlist_t`, `evch_qelem_t`, `evch_squeue_t`
  - callback typedefs
  - `evch_gevent_t`, `evch_eventq_t`, `evch_evqsub_t`, `evch_subd_t`, `evch_chan_t`, `evch_bind_t`, `evchanq_t`
- User-channel private APIs for open, close, allocate, post, subscribe, control, unsubscribe, channel data, properties, and walking queued events.
- Driver ioctl constants and packed argument structures:
  - `SEV_PUBLISH`, `SEV_CHAN_OPEN`, `SEV_CHAN_CONTROL`, `SEV_SUBSCRIBE`, `SEV_UNSUBSCRIBE`, `SEV_CHANNAMES`, `SEV_CHANDATA`, property ioctls
  - `sev_bind_args_t`, `sev_control_args_t`, `sev_publish_args_t`, `sev_subscribe_args_t`, `sev_unsubscribe_args_t`, `sev_chandata_args_t`, `sev_propnvl_args_t`

## Dependencies And Relationships
Includes `sys/nvpair.h`, `sys/id_space.h`, and `sys/door.h`. It backs the public API in `sysevent.h` and the `/dev/sysevent` driver/userland protocol.

## Research Notes
The comments warn not to alter packed structures without careful testing. Layout is intentionally 64-bit aligned, with pack pragmas for cross-ABI structure compatibility where needed.
