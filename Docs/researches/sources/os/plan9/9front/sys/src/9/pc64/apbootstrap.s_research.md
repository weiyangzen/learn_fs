# File Research: sources/os/plan9/9front/sys/src/9/pc64/apbootstrap.s

Application Processor bootstrap code for amd64 multiprocessor startup. It is copied below 1MB at `APBOOTSTRAP` and entered by APs in real mode.

Key behavior:
- Starts in 16-bit real mode, normalizes segment registers, loads a temporary GDT, enables protected mode, and far-jumps to 32-bit code.
- 32-bit path loads the AP PML4 physical address, configures CR4 for PAE/PGE, enables long mode through EFER, enables paging/write-protect in CR0, and far-jumps into 64-bit code.
- 64-bit path loads the virtual GDT pointer, clears long-mode-ignored segment registers, clears LDTR, sets `m` and `up`, sets the AP stack from `_apmach`, and calls the C AP startup vector.
- Exposes fixed data slots `_apvector`, `_appml4`, `_apapic`, `_apmach`, and `_apefer` used by `mpstartap`.
- Defines temporary 64-bit and 32-bit descriptors plus physical/virtual GDT pointers.

Notable dependencies:
- Constants from `mem.h`, especially selectors, `KZERO`, `MACHSIZE`, and AP bootstrap address assumptions.
- `squidboy.c` fills the bootstrap data slots before starting the AP.

Research notes:
- The comments note the code is further restricted to the first 64KB due to shortcuts in the real-mode setup.
- It halts forever if the C AP startup vector ever returns.
