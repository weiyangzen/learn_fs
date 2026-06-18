# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/pccard.h

## Purpose
Acts as the master include header for PCMCIA PC Card client drivers.

## Main Interfaces
This file primarily aggregates dependencies rather than defining its own data model. It includes:
- Generic kernel/user headers:
  - `sys/types.h`
  - `sys/param.h`
  - `sys/kmem.h`
- Kernel-only support:
  - `sys/systm.h`
  - `sys/sysmacros.h`
  - `sys/cmn_err.h`
  - `sys/debug.h`
  - `sys/devops.h`
- DDI/module headers:
  - `sys/dditypes.h`
  - `sys/modctl.h`
- PC Card/Card Services headers:
  - `sys/pctypes.h`
  - `sys/cs_types.h`
  - `sys/cis.h`
  - `sys/cis_handlers.h`
  - `sys/cs.h`

## Dependencies And Relationships
All PC Card client drivers include this to obtain Card Information Structure and Card Services types in a consistent order.

## Research Notes
No functions or structures are introduced directly; its role is include normalization for legacy PC Card driver code.
