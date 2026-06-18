# File Research: sources/virtualization/spdk/lib/nvme/nvme_io_msg.c

This file implements an external I/O message bridge that lets modules such as CUSE queue work into a controller-owned SPDK I/O context.

`nvme_io_msg_send()` allocates `struct spdk_nvme_io_msg`, fills controller, NSID, function pointer, and argument, then enqueues it on `ctrlr->external_io_msgs` under `external_io_msgs_lock`. The ring is multi-producer/single-consumer. Enqueue failure frees the message and returns `-ENOMEM`.

`nvme_io_msg_process()` is the single-consumer polling function. It only runs in the primary process, returns early when the ring or external qpair is unavailable or reset preparation is active, applies deferred producer updates, processes completions on `external_io_msgs_qpair`, dequeues up to eight messages, calls each message function, frees the message, and returns the number processed.

Producer registration is tracked with `struct nvme_io_msg_producer` entries in `ctrlr->io_producers`. `nvme_io_msg_ctrlr_register()` rejects null producers and duplicates, initializes the mutex, creates a 65536-entry SPDK ring, allocates an I/O qpair, and inserts the first producer. If producers are already registered or the controller is resetting, it only appends the producer because messaging is already started or will be handled later.

`nvme_io_msg_ctrlr_update()` calls every registered producer’s `update()` callback in the primary process. If invoked from a secondary process, it sets `needs_io_msg_update` so the primary-side process loop performs the update later. `nvme_io_msg_ctrlr_detach()` stops all producers, removes them, frees the ring and external qpair, and destroys the mutex. `nvme_io_msg_ctrlr_unregister()` removes a specific producer and detaches the infrastructure when the producer list becomes empty.

Important invariants are single-threaded processing per controller, primary-process ownership of the qpair/ring consumer, correct ring lifetime relative to producer callbacks, and lock ordering when unregistering triggers detach and producer `stop()` callbacks while controller state is being modified.
