# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fibre-channel/fca/emlxs/emlxs_fcf.h

Purpose: Defines the SLI4/FCoE fabric-control object model and state machines for FCF tables, FCFI, VFI, VPI, RPI, and XRI resources.

Key definitions:
- Limits: `FCFTAB_MAX_FCFI_COUNT` and `FCFI_MAX_VFI_COUNT` are both 1 in this driver.
- Event IDs distinguish internal state entry, external fabric events, table online/offline, and FCFI/VFI/VPI/RPI online/offline/pause/resume events.
- Reason codes record why state transitions happen, including event/requested/no mailbox/no buffer/send failure/mailbox failure/no resource/not allowed/invalid.
- `XRIobj_t`: exchange resource with free-list links, XRI, state, SGL, segment, RPI bindings, owning packet, RX ID, flags, and exchange type.
- `emlxs_deferred_cmpl_t`: stores deferred completion context for port/node and three opaque args.
- `RPIobj_t`: remote port identifier state machine with index/RPI, previous/current reason and state, flags, attempts, XRI count, idle timer, owning VPI, node DID/service parameters, and deferred completion.
- `VPIobj_t`: virtual port identifier state machine, fabric/p2p RPIs, bound port, parent VFI, counts of online/paused RPIs, and port-bind flags.
- `VFIobj_t`: virtual fabric instance state machine, service parameters, parent FCFI, online VPI/logi counts, and FLOGI VPI pointer.
- `FCFIobj_t`: FCF instance state with FCF index, VLAN, generation, event tag, validity/availability/configuration/selection flags, `FCF_RECORD_t`, priority, and VFI count.
- `VFTable_t`: VFI table state and active/count/table pointer.
- `FCFTable_t`: top-level fabric table state, with separate FCoE and FC state values, request flags, online FCFIs, table pointers/counts, and timers.

Dependencies and interactions:
- Used directly inside `emlxs_sli4_t` and `emlxs_port_t` from `emlxs_fc.h`.
- `emlxs_extern.h` declares the notification and helper functions that drive these state machines.
- Depends on `MATCHMAP`, `SERV_PARM`, `emlxs_buf_t`, `emlxs_port`, `emlxs_node`, and `FCF_RECORD_t`.

Implementation notes:
- The file is declarative and state-machine oriented.
- Object flags encode both request state and derived state; implementation must keep counters and flags synchronized across nested FCFI/VFI/VPI/RPI/XRI ownership.
