# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/clients/of/sol_uverbs/sol_uverbs_event.h

This sol_uverbs event header declares async/completion event-file lifecycle, event cleanup, async HCA event handling, and event-file read/poll operations.

API surface:
- Allocate and release event files.
- Handle asynchronous IBT HCA events.
- Release CQ completion-channel association.
- Release queued user events for CQs, QPs, and SRQs.
- Close, read, and poll event files.

Risk-sensitive invariants:
- Event files back both async and completion channels and must wake pollers/blocking readers correctly.
- Resource destruction must remove object-specific pending events to avoid dangling pointers.
- Async events interact with HCA callbacks and user-visible event descriptors.
