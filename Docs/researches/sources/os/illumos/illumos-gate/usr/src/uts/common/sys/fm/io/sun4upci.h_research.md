# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fm/io/sun4upci.h

This header defines FMA event and payload names for sun4u PCI host bridges and related interconnects.

Platform/device class names:
- PCI host bridge families include Psycho (`"psy"`), Schizo (`"sch"`), Tomatillo (`"tom"`), and XMITS.

Ereport classes:
- PBM errors include target timeout, retry limit, secondary master/target/parity cases, and target-side PBM errors.
- Schizo/Tomatillo errors include MMU, bus unusable, slot lock, streaming buffer, and Tomatillo MMU bad/protection/invalid/timeout/UE cases.
- Psycho-specific class includes streaming buffer error.
- ECC memory errors distinguish DMA read/write and PIO UE/CE cases, including secondary variants.
- Safari events cover parity, unmapped/timeout/bus/status errors, bad commands, SSM disabled, PLL, queue timeouts, and CPU parity/bidi cases.
- JBus events cover parity, illegal byte/coherence, snoop errors, bad command, unmapped, timeout, bus, and PCI-related snoop cases.

Payload fields:
- PBM register/log fields.
- IOMMU control and fault address fields.
- ECC error state, syndrome, type, disposition, unum, and memory resource.
- Safari register/log/resource fields.
- JBus register/log/resource fields.

Dependencies and relationships:
- Platform-specific FMA protocol header for older SPARC PCI platforms.
- Complements generic PCI FMA naming in `sys/fm/io/pci.h`.
