# File Research: sources/os/linux/linux/block/bsg-lib.c

## Scope

This file provides the helper library for block SCSI generic transport queues built on blk-mq. It maps SG_IO v4 requests into `bsg_job`s, manages job lifetime and completion, and creates/removes bsg request queues for lower-level drivers.

## Core State and APIs

- `struct bsg_set` wraps a blk-mq tag set, registered `bsg_device`, driver job callback, and timeout callback.
- `bsg_transport_sg_io_fn()` handles SCSI transport `sg_io_v4` commands:
  - validates protocol/subprotocol and `CAP_SYS_RAWIO`;
  - allocates request(s), including bidirectional data-in requests when needed;
  - copies the user request buffer;
  - maps user data buffers with `blk_rq_map_user()`;
  - executes the request synchronously with `blk_execute_rq()`;
  - fills SG status/residual/reply fields;
  - unmaps/free all request resources.
- Job lifetime:
  - `bsg_job_get()` and `bsg_job_put()` wrap `kref` handling.
  - `bsg_teardown_job()` releases the device reference, frees sg lists, and ends the request.
  - `bsg_job_done()` stores result/reply length and completes the request unless fake timeout injection suppresses completion.
- Queue operation:
  - `bsg_prepare_job()` maps request and reply payload scatterlists and takes a device reference.
  - `bsg_queue_rq()` starts the request, prepares the job, invokes the driver `job_fn`, and returns blk status.
  - `bsg_complete()` drops the job reference on softirq completion.
  - `bsg_timeout()` delegates to the optional driver timeout callback.
- Queue lifecycle:
  - `bsg_setup_queue()` allocates `bsg_set`, configures one blocking blk-mq hardware queue, allocates the queue, sets default SG timeout, and registers a bsg char device.
  - `bsg_remove_queue()` unregisters the bsg device, destroys the queue, drops queue refs, frees the tag set, and frees `bsg_set`.

## Dependencies and Invariants

- Depends on blk-mq, bsg core registration, SCSI SG v4 structures, scatterlist mapping, and timeout fault injection.
- Each allocated request has per-request `bsg_job` private data with a persistent sense/reply buffer from `bsg_init_rq()`/`bsg_exit_rq()`.
- Drivers must call `bsg_job_done()` when asynchronous jobs complete.
- Bidirectional jobs carry a separate `bidi_rq`/`bidi_bio` that must be unmapped and freed independently.
