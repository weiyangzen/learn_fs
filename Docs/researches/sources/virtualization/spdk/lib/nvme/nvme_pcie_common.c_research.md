# File Research: sources/virtualization/spdk/lib/nvme/nvme_pcie_common.c

## Purpose

Implements the shared PCIe/vfio-user qpair mechanics: queue allocation/reset, admin and I/O qpair create/delete commands, tracker lifecycle, submission/completion processing, PRP/SGL/metadata mapping, poll-group support, and PCIe tracepoint registration.

## Main Responsibilities

- Allocate submission/completion rings, optionally using CMB submission queues, and create tracker arrays sized to avoid CQ wrap issues.
- Maintain PCIe qpair state, queue indices, phase bits, free/outstanding tracker queues, retry counts, and statistics.
- Build and submit NVMe admin commands to create/delete I/O CQs/SQs.
- Handle asynchronous qpair connection state through create-CQ/create-SQ completion callbacks.
- Submit trackers by copying commands into SQ entries, handling fused command doorbell suppression and QEMU maximum access-width quirks.
- Process completions from CQ phase bits, prefetch next tracker, apply architecture barriers, complete or retry requests, ring CQ/SQ doorbells, and run timeout checks.
- Abort outstanding trackers/AERs and manually complete failed requests.
- Delete qpairs, clear shadow doorbells, wait for delete queue admin completions, complete remaining I/O, and free owned resources.
- Build request data pointers using PRP or hardware SGLs for contiguous, callback-SGL, and IOV payloads; map metadata through MPTR or metadata SGL where supported.
- Implement PCIe transport poll group completion processing and stats.

## Key Control Flow

`nvme_pcie_qpair_submit_request()` obtains a free tracker, links it to the request, assigns CID, decides PRP vs SGL based on controller flags/admin queue/opcode quirks, builds payload and metadata mappings, then calls `nvme_pcie_qpair_submit_tracker()`. If mapping fails, completion is deferred through `nvme_pcie_fail_request_bad_vtophys()` so callers see failure via callback rather than synchronous submission failure.

`nvme_pcie_qpair_process_completions()` handles connecting qpairs specially by polling adminq until create commands finish. For normal queues it scans completions by phase, completes trackers, updates stats and doorbells, flushes delayed SQ doorbells, checks timeouts, completes cross-process admin requests, and drains pending vtophys failures.

## Integration Points

Uses `nvme_pcie_internal.h` for transport-private layout and doorbell helpers, generic request/qpair/controller code from `nvme_internal.h`, SPDK env vtophys/memory APIs, trace APIs, and SGL helpers.

## Risk Notes

- The mapping path is dense and assertion-heavy; malformed or unexpected payload type/shape can trip asserts in debug builds.
- Completion handling asserts if a CQE CID does not map to an outstanding tracker, which is appropriate for corruption but fatal.
- Bad vtophys failures are deferred when outside completion context, so tests need to cover delayed failure completion.
