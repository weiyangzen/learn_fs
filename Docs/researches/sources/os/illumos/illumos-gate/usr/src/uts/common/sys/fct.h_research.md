# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fct.h

## Role

`fct.h` defines the common Fibre Channel Target framework interface between STMF/FCT and Fibre Channel adapter drivers. It covers target port, remote port, command, ELS/CT/ABTS, data buffer store, link info, port attributes/statistics, control commands, and FCT service functions.

## Core Objects

- Defines `fct_struct_id_t` values for allocating local ports, remote ports, received/solicited ELS, solicited CT, received ABTS, FCP exchanges, and data-buffer stores.
- `fct_remote_port_t` stores FCT/FCA private data, local port pointer, node/port WWN strings and bytes, remote id, hard address, and handle.
- `fct_cmd_t` stores FCT/FCA/private command data, local/remote port, link pointer, command type, remote-port handle, command handle, local/remote port ids, exchange ids, and completion status. Helper macros extract slot index and validity from command handles.
- Defines command type bits for FCP exchange, received ELS, solicited ELS, received ABTS, solicited CT, and all types.
- `fct_els_t`, `fct_sol_ct_t`, and `fct_rcvd_abts_t` define payload buffers and ABTS response state.

## Ports, Buffers, And Link State

- Defines FC-HBA string lengths, FCT info/taskq lengths, and `FC_TGT_PORT_RLS`.
- `fct_port_attrs_t` contains manufacturer, serial, model, model description, hardware/driver/option ROM/firmware versions, driver name, vendor-specific id, supported class/speed, and max frame size.
- `fct_port_link_status_t` and `fct_port_stat_t` track link failure/sync/signal/protocol/invalid word/CRC counters.
- `fct_dbuf_store_t` wraps STMF data buffer storage callbacks for allocation, free, setup, teardown, max SGL transfer, and copy threshold.
- `fct_local_port_t` stores private data, STMF local port, WWNs and symbolic names, provider, address/login/exchange limits, FCA private sizes, abort timeout, data buffer store, and FCA operation callbacks for link info, remote port registration, command send/data/response/abort, control, FLOGI exchange, HBA details, and port info.
- `fct_flogi_xchg_t` and `fct_link_info_t` describe FLOGI exchanges and link topology/speed/FLOGI ownership state.

## Control And API

Defines port topology/speed constants, port states, FCT control commands for online/offline/force LIP and completion acknowledgement, and I/O flags for FCA-done handling. `FCT_FILL_CTIU_PREAMBLE()` initializes common CT IU bytes.

Exports conversion, allocation/free, SCSI task allocation, local port registration/deregistration, event handling, command posting/termination, handle lookup, control dispatch, completion paths, port initialize/shutdown, received FLOGI handling, event logging, and WWN string conversion.
