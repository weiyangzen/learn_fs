# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/contract_impl.h

`contract_impl.h` is the main private kernel contract framework header. It defines 32-bit event/status/param forms, kernel parameter wrappers, template operation vectors, templates, queue selection and flags, acknowledgement outcomes, event queues, members, kernel events, contract vnode tracking, contract operation vectors, contract types, contract flags, time accounting, core contract state, and listener state.

It declares template operations, parameter copyin/copyout, contract lifecycle and adoption/abandon/ack functions, event publication and listener management, lookup/ownership helpers, type-level queries, vnode association helpers, and default invalid/notsupported acknowledgement stubs. It is the internal coordination layer for process and device contracts.
