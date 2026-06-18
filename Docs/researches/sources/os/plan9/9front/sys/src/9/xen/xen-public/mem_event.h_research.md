# File Research: sources/os/plan9/9front/sys/src/9/xen/xen-public/mem_event.h

Imported Xen public memory-event ring ABI.

Purpose:
- Defines common request/response structures for Xen memory event mechanisms such as paging, access violations, sharing, and introspection.

Key content:
- Includes `xen.h` and generic `io/ring.h`.
- Defines memory event flags for VCPU paused, drop page, eviction failure, foreign, and dummy.
- Defines memory event reasons for unknown, access violation, CR0, CR3, CR4, INT3, single-step, and MSR.
- Defines `mem_event_request_t`/`mem_event_response_t` with flags, VCPU ID, GFN, offset, guest linear address, p2m type, access bits, GLA validity, and reason.
- Generates `mem_event` ring types.

Integration:
- Used by `domctl.h` memory-event setup/control structures.
- Not used by visible 9front guest runtime.

Risks/notes:
- Blocking memory-event users can pause VCPUs pending response; incorrect handlers can deadlock guests.
- Bitfields and ring layout must match Xen/tool expectations.
