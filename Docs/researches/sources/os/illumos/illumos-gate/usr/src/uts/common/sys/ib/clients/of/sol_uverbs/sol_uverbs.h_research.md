# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ib/clients/of/sol_uverbs/sol_uverbs.h

This Solaris user-verbs kernel-agent header defines the main sol_uverbs module context and all user resource objects exposed to OFED user verbs.

Core definitions:
- Minor layout supports up to 16 HCA minors plus event and max minor constants.
- `uverbs_event_t` wraps async/completion event descriptors, event-file linkage, object linkage, and an event counter.
- `uverbs_module_context_t` stores global IBT client registration, HCA GUID/list state, HCA records, device info, and event device node.
- `uverbs_ufile_uobj_t` represents async/completion event files with refcount, poll state, owning context, event list, CQ notification control, and CQ count.
- `uverbs_uctxt_uobj_t` tracks an opened HCA/user context and all owned PD/MR/CQ/QP/SRQ/AH lists plus async/completion event files.
- Resource objects wrap PDs, MRs, CQs, SRQs, AHs, and QPs with IBTF handles, context list entries, event tracking, dependency counts, and free-pending state.
- Extern user-object tables provide global ID lookup for each resource class.

API surface:
- Command handlers for context, PD, AH, device/port/GID/PKey query, MR registration, completion channel creation, and status/capability conversions.
- Free helpers for PD/QP/SRQ/CQ and inline typed lookup helpers for read/write access.

Risk-sensitive invariants:
- User context lists are cleanup ownership lists; object tables are the authoritative lookup path.
- QP objects retain dependency handles for PD/CQ/SRQ and coordinate with UCMA through QP free state and CQ notification control.
- Event counters and object event lists must be drained on resource destruction.
