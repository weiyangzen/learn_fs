# File Research: sources/os/plan9/9front/sys/src/9/pc/mtrr.c

Implements x86 MTRR cache-type management and reporting. It reads fixed and variable MTRRs, constructs effective cache-type ranges, updates registers safely, and synchronizes changes across CPUs.

Key behavior:
- Defines MSR constants for variable MTRRs, default MTRR type, capabilities, and AMD K8 `TOM2` handling.
- `State` captures MTRR mask, capability/default registers, fixed registers, variable registers, and AMD top-of-memory state.
- `Range` describes effective physical ranges and cache types: uncacheable, write-combining, write-through, write-protected, and write-back.
- `gettype()` and `getnext()` compute effective memory type transitions from fixed, variable, default, and TOM2 rules.
- `getstate()` reads hardware MTRR state and detects usable support.
- `putstate()` updates MTRRs using the required sequence: raise IPL, disable cache, flush, disable PGE, disable MTRRs, write registers, flush again, re-enable MTRRs/cache/PGE.
- `mtrr()` validates and adds a requested cache range, tries to synthesize satisfiable fixed/variable register programming, and triggers CPU-wide synchronization.
- `mtrrattr()` and `mtrrprint()` expose current cache attributes.
- `mtrrclock()` runs from clock interrupts as a CPU barrier and applies pending MTRR state to all processors.
- `mtrrsync()` initializes CPU0 state or applies CPU0 state to other CPUs during identification.

Research notes:
- `screen.c` calls `mtrr(..., "wc")` for framebuffer write-combining after `vmap()`.
- The range fitting logic is conservative: it rejects unsatisfiable or unaligned ranges and checks the synthesized state before committing.
- CPU synchronization uses static `Ref` barriers and assumes all active CPUs pass through `mtrrclock()`.
