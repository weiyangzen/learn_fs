# File Research: sources/virtualization/nvme-cli/libnvme/src/nvme/mi.c

Core NVMe-MI implementation: endpoint lifecycle, MI/Admin message submission, controller scanning, quirk handling, status parsing, and AEM state machine.

Key behavior:
- Parses `mctp:<net>,<eid>` and `mctp:<net>,<eid>:<ctrl-id>` device names.
- Initializes MI transport handles and closes MI controller handles.
- Probes endpoints once for model-specific quirks unless disabled in the global context.
- Uses an Identify Controller command via MI to detect a Samsung model requiring a minimum inter-command delay.
- Implements endpoint initialization with default timeout, endpoint/controller lists, and submit hooks.
- Creates controller transport handles under an MI endpoint.
- Scans endpoints by issuing Read MI Data Controller List and creating handles for returned controller IDs.
- Calculates and verifies MI MIC using CRC32C-like update logic.
- Central `libnvme_mi_submit()`:
  - validates header alignment and sizes
  - invokes submit-entry hook
  - performs quirk probing
  - calculates MIC
  - inserts quirk delay when needed
  - calls transport submit
  - validates MIC, message type, response direction, and command slot
  - invokes submit-exit hook
- Provides raw admin transfer and passthrough support over MI, including NVMe-MI DLEN/DOFF limits and no bidirectional transfer support.
- Provides Control Primitive execution.
- Provides MI command helpers:
  - raw MI transfer
  - Read MI Data subsystem/port/controller-list/controller-info
  - Subsystem Health Status Poll
  - Configuration Get/Set
  - Asynchronous Event configuration Get/Set
- Closes endpoints by closing child transport handles, invoking transport close, unlinking from global context, and freeing.
- Implements MI status string mapping.
- Implements AEM bitfield helpers and validation helpers.
- Implements AEM enable/disable/process flow:
  - opens AEM transport path
  - disables preexisting enabled events
  - enables requested event IDs
  - validates occurrence lists
  - stores callback context
  - exposes pollable fd
  - lets callbacks iterate events with `libnvme_mi_aem_get_next_event()`
  - ACKs events when callback requests `NVME_MI_AEM_HNA_ACK`

Research notes:
- MI returns use mixed conventions: negative errno-style errors for local/transport/protocol problems and NVMe/MI status values for device responses.
- Admin passthrough enforces 4096-byte data length and rejects bidirectional transfers.
- AEM processing uses an internal context whose event payload pointers are valid only during callback processing.
- Duplicate AEM generation numbers are treated as no new events.
