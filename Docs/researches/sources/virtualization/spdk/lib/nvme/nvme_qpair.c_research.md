# File Research: sources/virtualization/spdk/lib/nvme/nvme_qpair.c

## Purpose

Implements generic NVMe qpair behavior above individual transports: command/completion formatting, status string lookup, retry classification, queued request abort/resubmission, completion processing wrapper, qpair initialization/deinitialization, submission state machine, error injection, and public qpair accessors.

## Main Responsibilities

- Convert admin, fabrics, I/O, feature, SGL, and completion status values to diagnostic strings.
- Print commands and completions, including opcode-aware fabric command status via newer `_ext` APIs.
- Define qpair state names and retry policy for selected generic/path status codes.
- Manually complete requests for abort/error paths and abort queued requests with or without matching callback arg.
- Handle qpair enable transitions after connect/reset, including PCIe-specific abort of old queued/outstanding requests during reset.
- Process completions through transport callbacks while handling admin register completions, transport events, failed controllers, error injection, completion-context deletion, and queued request resubmission.
- Initialize qpair request pools, including a reserved request, free/queued/aborting/error queues, transport type, state fields, and async flag.
- Deinitialize by aborting queued/error requests and freeing request/error command allocations.
- Submit requests through `_nvme_qpair_submit_request()`, including split parent/child handling, queued request preservation, fabrics connect exceptions, reset queuing, and error cleanup.
- Add/remove command error injection entries.

## Key Control Flow

`spdk_nvme_qpair_process_completions()` is the generic completion entry point. It handles admin-only register and transport events, checks controller/qpair state, completes injected errors, calls the transport completion function inside completion context, handles deferred qpair deletion, then resubmits as many queued requests as completions processed.

`nvme_qpair_submit_request()` sets timeout state, preserves FIFO ordering if queued requests already exist, calls `_nvme_qpair_submit_request()`, and queues on `-EAGAIN`.

## Integration Points

Depends on transport ops, controller state/locking helpers, request allocation/completion helpers, SPDK logging/deprecation, OCSSD opcodes, and public qpair APIs.

## Risk Notes

- Submission, reset, and reconnect paths are state-machine-sensitive, especially around PCIe reset exceptions and split requests.
- Error injection changes normal request flow and requires cleanup in qpair deinit.
- Completion callbacks may submit or abort more requests, so abort paths deliberately avoid recursive completion loops.
