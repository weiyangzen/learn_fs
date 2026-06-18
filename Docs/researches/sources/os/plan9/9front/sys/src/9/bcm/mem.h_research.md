# File Research: sources/os/plan9/9front/sys/src/9/bcm/mem.h

32-bit BCM memory map, page constants, register conventions, and PTE flags.

Key contents:
- Defines page size, stack sizes, max CPUs, `Mach` layout, and ARM register assignments.
- Defines kernel/user virtual layout: `KZERO`, `KTZERO`, `USTKTOP`, `FRAMEBUFFER`, `VIRTIO`, `ARMLOCAL`, and boot scratch addresses.
- Defines page table sizing and segment-map constants.
- Defines Plan 9 PTE abstraction bits: valid, writable, uncached, no-exec, and physical page mask.
- Defines `PHYSDRAM`, min/max macros, and alignment helpers.

Role:
- Central ABI contract for BCM C and assembly files.

Notable constraints:
- Low physical/virtual addresses are tightly reserved for vectors, `Mach`, page tables, mailbox buffer, FIQ stack, and reboot code.
