# File Research: sources/virtualization/spdk/lib/nvme/nvme_ctrlr_cmd.c

This file implements SPDK NVMe controller-level command wrappers. It builds and submits raw I/O commands, raw admin commands, Identify, namespace management, feature get/set, log page retrieval, aborts, firmware operations, security send/receive, sanitize, and directive send/receive.

Raw I/O entry points allocate `nvme_request` objects on the supplied qpair and copy a caller-provided `spdk_nvme_cmd` into the request. `spdk_nvme_ctrlr_io_cmd_raw_no_payload_build()` is PCIe-only and uses a no-payload request. `spdk_nvme_ctrlr_cmd_io_raw()` uses a contiguous payload. The metadata variants compute metadata length from the command NSID namespace geometry when a metadata buffer is present, and the SGL raw path rejects missing reset/next-SGE callbacks.

Admin commands are serialized with `nvme_ctrlr_lock()`. Most allocate either a user-copy request or null request on `ctrlr->adminq`, fill opcode-specific CDWs, submit through `nvme_ctrlr_submit_admin_request()`, then unlock. User-copy direction is significant: Identify, Get Features, Get Log Page, Security Receive, and Directive Receive are controller-to-host; Set Features, namespace attach/detach/create, firmware image download, Security Send, and Directive Send are host-to-controller.

Identify support is centralized in `nvme_ctrlr_cmd_identify()`, which sets CNS, CNTID, NSID, and CSI. Namespace management helpers wrap Namespace Attachment and Namespace Management opcodes for attach, detach, create, and delete. Format, doorbell-buffer config, Number of Queues, async event config, and Host Identifier are small command builders on top of the same admin submission path.

Log page retrieval validates nonzero payload size and 4-byte-aligned offset. If an offset is requested, the controller must advertise extended data support through `ctrlr->cdata.lpa.lpeds`. The function converts byte count to NUMD, splits offset into LPOL/LPOU, accepts caller-supplied extra CDW fields, and has a simpler wrapper that passes zeros for the extension fields.

Abort handling is the most stateful part of the file. `_nvme_ctrlr_submit_abort_request()` limits concurrent aborts by the controller ACL value and queues excess aborts in `ctrlr->queued_aborts`. Abort completions decrement `outstanding_aborts` and retry queued aborts unless the controller/admin qpair is failing. `spdk_nvme_ctrlr_cmd_abort_ext()` creates a parent abort request, iterates outstanding requests on a qpair, adds child abort commands for requests matching a callback argument, separately aborts queued requests with the same callback argument, and completes the parent when all child aborts finish.

The firmware, security, sanitize, and directive helpers are thin but preserve NVMe wire encodings: firmware download uses NUMD and DWORD offset, security commands split SPSP into fields and use payload size in CDW11, sanitize copies the sanitize structure into CDW10, and directives encode DOPER/DTYPE/DSPEC plus optional CDW12/CDW13.

Important invariants are request ownership, admin lock coverage, correct user-copy direction, and abort accounting. Any change to abort paths must maintain `outstanding_aborts`, queued abort retry behavior, child-parent completion, and request freeing. Metadata raw commands assume a valid namespace and nonzero sector size when metadata is supplied.
