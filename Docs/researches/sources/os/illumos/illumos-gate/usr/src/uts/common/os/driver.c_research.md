# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/driver.c

## Purpose

`driver.c` contains core illumos driver entry-point dispatch helpers. It wraps nexus and leaf driver callbacks for identify/probe/attach/detach/reset/quiesce, basic block/character device operations, layered open/close through specfs, size-property queries, and property operations.

The file is intentionally thin: it centralizes common DDI/DKI dispatch mechanics and auxiliary integration with power management, MDI, DTrace I/O probes, and specfs open/close semantics.

## Configuration Entry Points

- `devi_identify()` calls `devo_identify` if present.
- `devi_probe()` calls `devo_probe`, defaulting to `DDI_PROBE_DONTCARE` for self-identifying devices without a probe routine, and wraps probe with PM pre/post hooks.
- `devi_attach()` runs MDI pre/post attach, PM attach hooks, parental resume shortcuts, parent attach ctlops, and the driver's `devo_attach`.
- `devi_detach()` validates detach command shape, supports parental suspend shortcuts, runs MDI/PM hooks, parent detach ctlops, and the driver's `devo_detach`.
- `devi_reset()` and `devi_quiesce()` call optional reset/quiesce entry points.

`i_attach_ctlop()` and `i_detach_ctlop()` package attach/detach state into `attachspec` or `detachspec` and send `DDI_CTLOPS_ATTACH` or `DDI_CTLOPS_DETACH` to the parent.

## Leaf Device Open And Close

`dev_open()` and `dev_close()` directly dispatch to `cb_open` and `cb_close`; comments direct newer code to use the LDI interfaces instead.

`dev_lopen()` and `dev_lclose()` are the layered open/close helpers. They create a specfs vnode with `makespecvp()`, call `VOP_OPEN` or `VOP_CLOSE` with `FKLYR`, and rely on specfs for open/close exclusion and last-close behavior. `dev_lopen()` places an extra hold on the common vnode containing the open count. `dev_lclose()` releases that hold carefully and diagnoses extra closes without necessarily panicking on production kernels.

The `dev_lclose_ce` tunable controls the severity of extra-close diagnostics: panic in debug kernels by default, warning otherwise.

## Device Operations

Block-device wrappers:

- `bdev_strategy()` fills `bp->b_dip`, fires `io:::start`, marks `B_STARTED`, and calls `cb_strategy`.
- `bdev_print()` dispatches `cb_print`.
- `bdev_size()` reads 32-bit `nblocks` and block-size properties and returns DEV_BSIZE block count.
- `bdev_Size()` does the same for 64-bit `Nblocks`.
- `bdev_dump()` dispatches `cb_dump`.

Character-device wrappers:

- `cdev_read()`, `cdev_write()`, `cdev_ioctl()`, `cdev_devmap()`, `cdev_segmap()`, and `cdev_poll()` dispatch through `cb_ops`.
- `cdev_mmap()` calls a supplied mmap function pointer.
- `cdev_size()` and `cdev_Size()` query `size` or `Size` properties for non-STREAMS character drivers without forcing unused drivers into memory.
- `cdev_prop_op()` dispatches `cb_prop_op`.

## Instance Lookup

`dev_to_instance()` loads the driver for a major number with `mod_hold_dev_by_major()`, requires `devo_getinfo`, asks the driver to translate `DDI_INFO_DEVT2INSTANCE`, releases the module hold, and returns `-1` on failure.

## Dependencies

This file depends on `devopsp`, `devnamesp`, specfs snodes, DDI/NDI driver structures, PM hooks, MDI hooks, DTrace I/O probes, property helpers, and module hold/release routines.

## Notable Invariants And Audit Notes

- `devi_attach()` and `devi_detach()` pair MDI/PM pre and post notifications around driver entry points.
- `dev_lopen()` deliberately drops `OTYP_LYR` and uses `FKLYR` through specfs.
- `dev_lclose()` must preserve common-vnode accounting even when callers over-close; this path is intentionally defensive because double close indicates a driver bug.
- `bdev_size()` and `bdev_Size()` assume block-size properties are meaningful divisors/multipliers of `DEV_BSIZE`; callers needing byte sizes should prefer higher-level size helpers when available.
