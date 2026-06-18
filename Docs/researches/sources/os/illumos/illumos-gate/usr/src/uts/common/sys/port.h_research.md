# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/port.h

## Purpose
Defines the public event-port ABI: event sources, event records, notification records, file event objects, alert flags, and file-watch event masks.

## Main Interfaces
- Event sources:
  - `PORT_SOURCE_AIO`
  - `PORT_SOURCE_TIMER`
  - `PORT_SOURCE_USER`
  - `PORT_SOURCE_FD`
  - `PORT_SOURCE_ALERT`
  - `PORT_SOURCE_MQ`
  - `PORT_SOURCE_FILE`
- Structures:
  - `port_event_t`
  - `port_notify_t`
  - `file_obj_t`
- 32-bit variants under `_SYSCALL32`:
  - `file_obj32_t`
  - `port_event32_t`
  - `port_notify32_t`
- Alert flags:
  - `PORT_ALERT_SET`
  - `PORT_ALERT_UPDATE`
  - `PORT_ALERT_INVALID`
- File watch events:
  - `FILE_ACCESS`
  - `FILE_MODIFIED`
  - `FILE_ATTRIB`
  - `FILE_TRUNC`
  - `FILE_NOFOLLOW`
- File exception events:
  - `FILE_DELETE`
  - `FILE_RENAME_TO`
  - `FILE_RENAME_FROM`
  - `UNMOUNTED`
  - `MOUNTEDOVER`

## Dependencies And Relationships
Includes `sys/types.h`. Private kernel implementation details are split into `port_kernel.h` and `port_impl.h`.

## Research Notes
`port_event_t` is source-polymorphic: object and event meanings depend on `portev_source`.
