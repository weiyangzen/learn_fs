# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/portif.h

## Purpose
Defines the SCSI Target Mode Framework local-port/provider interface, including data-buffer stores, local/remote ports, sessions, provider callbacks, and registration APIs.

## Main Interfaces
- `stmf_dbuf_store_t`: data-buffer allocation/free/setup/teardown callbacks.
- `PORTIF_REV_1`: current port interface revision.
- `stmf_local_port_t`: local port identity, alias, provider, data-buffer store, abort timeout, and operations for transfer, status, task free, abort, polling, control, info, and events.
- `stmf_remote_port_t`: remote transport ID and size.
- `stmf_dflt_scsi_tptid_t`: default SCSI transport ID layout with endian-dependent bitfields.
- `STMF_LPORT_ABORT_TASK`: abort command.
- `stmf_port_provider_t`: provider metadata and callback.
- `STMF_SESSION_ID_NONE`
- `stmf_scsi_session_t`: session identity, local/remote ports, alias, and session ID.
- Registration/control:
  - `stmf_register_port_provider()`
  - `stmf_deregister_port_provider()`
  - `stmf_register_local_port()`
  - `stmf_deregister_local_port()`
  - `stmf_register_scsi_session()`
  - `stmf_add_rport_info()`
  - `stmf_remove_rport_info()`
  - `stmf_deregister_scsi_session()`
  - `stmf_set_port_standby()`
  - `stmf_set_port_alua()`

## Dependencies And Relationships
Includes `sys/stmf_defines.h` and references STMF data buffers, tasks, status codes, SCSI device descriptors, and transport IDs. `pppt_ic_if.h` uses STMF session and remote-port types for proxy/interconnect messages.

## Research Notes
The interface splits STMF-private and provider/private storage on buffers, ports, providers, and sessions.
