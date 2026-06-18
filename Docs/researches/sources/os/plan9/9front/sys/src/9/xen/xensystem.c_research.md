# File Research: sources/os/plan9/9front/sys/src/9/xen/xensystem.c

Purpose: Core 9front Xen kernel integration layer. It wraps Xen hypercalls, manages Xen-specific page-table operations, handles event-channel upcalls, grants/transfers frames, and implements interrupt masking/channel helpers.

Key behavior:
- Hypercall wrappers call `xencall1`-`xencall6` for MMU, sched, event channel, Xen version, console, grant table, and memory ops.
- Maintains Xen globals: `xenstart`, `HYPERVISOR_shared_info`, `patomfn`, `matopfn`, `hypervisor_virt_start`, `xentop`.
- Page-table helpers pin/unpin L1/L2/L3 tables, switch base pointer, flush TLB, and update PTEs with machine-address translations.
- Grant helpers: `acceptframe`, `donateframe`, `shareframe`.
- `xenupcall` drains pending event-channel bits and dispatches them through Plan 9 `trap` with vector `100+port`.
- Interrupt glue binds VIRQs/channels, masks/unmasks event-channel bits, and implements `spllo`, `splhi`, `splx`, `islo`.
- Channel helpers allocate unbound ports and notify peers; `halt` blocks via Xen scheduler when idle.

Integration notes: Depends on Xen public headers/types, Plan 9 MMU/trap/intr code, and assembly hypercall stubs in `xen.s`.

Risk/attention points: Several wrappers panic on failure. Comments note possible efficiency improvement via multicall and uncertainty about return-value handling. Event upcall masking is subtle and must preserve Xen pending/mask ordering.
