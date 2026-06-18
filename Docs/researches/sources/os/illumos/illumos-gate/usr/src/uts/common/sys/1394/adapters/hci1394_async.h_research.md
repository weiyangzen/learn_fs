# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/1394/adapters/hci1394_async.h

Private interface and state definitions for the IEEE 1394 OpenHCI asynchronous DMA engines. It covers outgoing requests/responses, incoming requests/responses, command tracking, queue handles, transaction labels, and race handling between request completion and response arrival.

Key elements:
- Defines descriptor/data buffer sizes for ATREQ, ARRESP, ARREQ, and ATRESP queues.
- Declares opaque `hci1394_async_handle_t`.
- Defines `hci1394_async_cstate_t` with `IN_PROGRESS`, `PENDING`, and `COMPLETED` states to handle races between ATREQ completion interrupts and ARRESP interrupts.
- `hci1394_async_cmd_t` stores:
  - service-layer command pointer and HAL/service private command state,
  - transaction label allocation state and label info,
  - ARREQ mblk ownership flag,
  - response/ack status and destination,
  - async command state,
  - backpointer to async state,
  - pending-list node,
  - queue command metadata used by `hci1394_q_at*()` routines.
- Warlock `_NOTE` annotations document fields used by only one thread or protected by scheme.
- `hci1394_async_t` stores pending-list, OHCI, tlabel, CSR, four queue handles, driver info, ARREQ flush state, PHY reset generation, and `as_atomic_lookup` mutex for ARRESP vs pending-timeout races.
- Declares lifecycle routines: `hci1394_async_init()`, `hci1394_async_fini()`, suspend/resume, command overhead query, flush/reset helpers, and pending-timeout update.
- Declares interrupt/queue processing routines for ATREQ, ARRESP, ARREQ, and ATRESP.
- Declares command submission routines for PHY, write, read, lock, and their response forms.
- Declares `hci1394_async_response_complete()` for freeing response-side ARREQ resources.

Dependencies:
- Depends on DDI headers, `h1394` service-layer command types, driver info, transaction list/label support, OHCI handle, CSR handle, and queue command/handle types.
- The queue comments tie this header directly to `hci1394_q` descriptor/data-buffer management and OpenHCI async DMA processing.

Research notes:
- The async command state exists specifically because hardware ordering and software interrupt observation can differ.
- ARREQ flush state is tied to bus reset processing; processing suppresses service-layer delivery until a current-generation PHY reset token is seen.
- The mblk ownership rule allows a target driver to keep received block-write data by nulling the command mblk before release.
