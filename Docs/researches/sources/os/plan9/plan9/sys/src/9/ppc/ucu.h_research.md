# File Research: sources/os/plan9/plan9/sys/src/9/ppc/ucu.h

UCU/Saturn board memory and PTE policy constants.

Key contents:
- Defines flash and memory sizing: 32 MiB main memory, no second memory bank, no flash `plan9.ini`.
- Defines Saturn MMIO base and 128 TLB entries.
- Defines PPC PTE policy bits for valid/write/read-only/uncached mappings.

Role:
- Selected by `mem.h` under `ucuconf` to specialize PPC memory layout and MMU policy.

Notable risks:
- Uses `FLASHMEM` and `PLAN9INI` as `~0`, intentionally signaling no usable flash config.
- The `PTEVALID` definition encodes write-through global cache policy.
