# File Research: sources/os/plan9/plan9/sys/src/9/pc/ahci.h

AHCI/SATA register, bit, and in-memory structure definitions.

Key contents:
- ATA error and status bit masks, including fatal error grouping.
- PCI AHCI BAR index.
- AHCI generic host control register layout `Ahba`.
- Host capability and global control flags.
- Port interrupt/status/error masks and fatal interrupt grouping.
- SATA SError bits and aggregate masks.
- Port command/control state bits and device-detection/interface-power states.
- AHCI port register layout `Aport`.
- Host memory structures:
  - `Afis` receive-FIS area descriptor,
  - `Alist` command list entry,
  - `Aprdt` PRD entry,
  - `Actab` command table,
  - `Aportm` software port state,
  - `Aportc` combined register/software pointer.

Role:
- Shared low-level hardware contract for an AHCI driver implementation.
- Contains no functions; it defines the symbolic interface to AHCI hardware and command memory.

Notable details:
- Some comments preserve AHCI spec section hints and note typo-like names from hardware docs.
- Command-table definition includes a single PRD entry, implying driver code may allocate/use one PRD per command table instance here.
