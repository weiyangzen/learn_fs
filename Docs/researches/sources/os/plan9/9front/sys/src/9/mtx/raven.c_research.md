# File Research: sources/os/plan9/9front/sys/src/9/mtx/raven.c

This file initializes the Motorola Raven PCI host bridge and MPIC interrupt controller for MTX. It defines a memory layout for Raven registers, configures address maps, swaps MPIC register endianness, and provides MPIC enable/disable/ack/eoi functions.

`raveninit` validates Raven vendor/device IDs, sets up four address windows for PCI memory, compatibility kernel/I/O mappings, and I/O slot 3, finds Raven’s PCI config device, computes the MPIC base, masks and routes 16 MPIC vectors to CPU 0, sets CPU task priority, and enables mixed mode so both 8259 and Raven interrupts are available.

`mpicenable`, `mpicdisable`, `mpicintack`, and `mpiceoi` are used by `trap.c` to route PCI and legacy interrupts.

Filesystem relevance is device infrastructure: PCI network/storage interrupt delivery and DMA windows rely on Raven setup.

Notable risks: address map assumptions must match `mem.h` and `PCIWADDR`; MPIC register access requires byte swapping; only 16 MPIC vectors are initialized.
