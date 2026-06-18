# File Research: sources/local-fs/xfsdump/inventory/Makefile

This makefile declares the inventory subsystem source inventory and hooks it into the shared build system.

Key content:
- Sets `TOPDIR = ..` and includes `$(TOPDIR)/include/builddefs`.
- `LSRCFILES` lists inventory implementation files and headers: `inv_api.c`, `inv_core.c`, `inv_fstab.c`, `inv_idx.c`, `inv_mgr.c`, `inv_oref.c`, `inv_oref.h`, `inv_priv.h`, `inv_stobj.c`, `inv_files.c`, `inventory.h`, `getopt.h`, and `testmain.c`.
- Defines empty `default install install-dev` targets.
- Includes `$(BUILDRULES)`.

Role:
- Provides build metadata for the inventory library/component consumed by dump content code for incremental/resume tracking.
