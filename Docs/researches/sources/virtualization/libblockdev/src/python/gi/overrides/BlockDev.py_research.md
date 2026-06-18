# File Research: sources/virtualization/libblockdev/src/python/gi/overrides/BlockDev.py

This Python file provides PyGObject overrides for libblockdev’s introspected `BlockDev` module. Its goals are more Pythonic constructors/default arguments, ergonomic extra command arguments, and richer exception classes.

Module setup:
- Imports the introspected `BlockDev` module through `gi.importer.modules`.
- Defines `bd_plugins`, mapping lowercase plugin names to `BlockDev.Plugin` enum values.
- Installs generic `__str__`, `__repr__`, and `__deepcopy__` behavior on all `GObject.GBoxed` subclasses in the module.
- `__repr__` renders size-like integer fields with `bytesize.Size`.

Boxed constructors and helper types:
- `PluginSpec` wraps `BlockDev.PluginSpec.new()`.
- `ExtraArg` wraps `BlockDev.ExtraArg.new()`.
- `FSMkfsOptions` creates an options object with Python defaults.
- `CryptoLUKSPBKDF`, `CryptoLUKSExtra`, `CryptoKeyslotContext`, and `CryptoIntegrityExtra` provide Python constructors for crypto boxed structs.
- `CryptoKeyslotContext` enforces exactly one of passphrase, keyfile, keyring, or volume key.

Extra argument handling:
- `_get_extra(extra, kwargs, cmd_extra=True)` accepts either a dict or list of `BlockDev.ExtraArg`.
- Additional keyword arguments become extra args.
- With `cmd_extra=True`, keyword names are prefixed with `--`; with `False`, names are passed as-is.
- Returns `None` if no extra args are present.

Function overrides:
- Adds defaults and keyword support for initialization, Btrfs, crypto, DM, loop, filesystem, LVM, MD RAID, s390 DASD, swap, partitioning, NVDIMM, and NVMe functions.
- Most wrappers save the original introspected function in a private variable, normalize defaults/extra args, and call the original.
- Filesystem and LVM wrappers dominate the file and mainly expose default arguments plus `extra`/`**kwargs`.
- Swap overrides include `swap_mkswap(device, label=None, uuid=None, extra=None, **kwargs)` and `swap_swapon(device, priority=-1)`.
- One-member enum workaround classes are defined for `DMTech`, `LoopTech`, `MDTech`, `SwapTech`, and `NVDIMMTech`.

Utility function:
- `plugin_specs_from_names(plugin_names)` converts a list of plugin name strings into `PluginSpec` objects using `bd_plugins`.

Exception model:
- `XRule` defines exception transformation rules.
- `ErrorProxy` lazily proxies plugin-prefixed functions and transforms exceptions.
- `BlockDevError` is the common base for libblockdev-specific Python exceptions.
- Plugin-specific exception classes include `BtrfsError`, `CryptoError`, `DMError`, `LoopError`, `LVMError`, `MDRaidError`, `MpathError`, `SwapError`, `PartError`, `FSError`, `S390Error`, `UtilsError`, `NVDIMMError`, `NVMEError`, and `SMARTError`.
- Swap has more granular subclasses for activation, old format, suspend image, unknown format, and page-size mismatch.
- `BlockDevNotImplementedError` maps GLib “function called, but not implemented” messages.
- Error proxies are exported as `btrfs`, `crypto`, `dm`, `loop`, `lvm`, `md`, `mpath`, `swap`, `part`, `fs`, `nvdimm`, `nvme`, `s390`, `smart`, and `utils`.

Research relevance:
- This file is the main compatibility/ergonomics surface for Python callers.
- It mirrors C error enum numeric codes in Python exception rules; changes to C enum ordering can break specific exception mapping.
- It makes `BlockDev.swap.swapon()` raise plugin-specific Python exceptions while `BlockDev.swap_swapon()` remains the raw introspected function.
- The `extra` keyword convention is a major bridge to C `BDExtraArg`.
