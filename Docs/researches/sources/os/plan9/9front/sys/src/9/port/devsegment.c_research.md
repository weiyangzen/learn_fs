# File Research: sources/os/plan9/9front/sys/src/9/port/devsegment.c

Purpose: Implements `#g`, a global segment device for creating named VM segments, configuring their address/size, attaching them through `segattach`, and reading/writing segment memory.

Key logic:
- Maintains up to 100 `Globalseg` objects with name, owner, permissions, refcount, and `Segio` state.
- Top-level create makes a named segment directory; each segment directory exposes `ctl` and `data`.
- `ctl` accepts `va base length`, plus eve-only `fixed` and `sticky` variants.
- Normal segments use `newseg(SG_SHARED)`; sticky segments allocate and prefill pages; fixed segments allocate a physically contiguous run of user pages.
- `data` reads and writes memory through `segio`.
- `globalsegattach` is installed into `_globalsegattach` so normal VM attach logic can resolve named global segments.

Dependencies and integration:
- Uses VM `Segment`, `Page`, `Pte`, `newseg`, `segpage`, `putseg`, `Segio`, physical segment name checks, and page allocator internals.

Risks and notes:
- Fixed segments require contiguous free pages and are eve-only.
- Segment names must not collide with physical segment names.
- Removing a segment clears the global slot, but open refs keep the underlying object alive until close.
