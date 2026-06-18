# File Research: sources/os/bsd/dragonflybsd/sys/vfs/ntfs/ntfs_subr.c

This is the core NTFS metadata and data-path helper implementation. It loads MFT records into `ntnode` attribute lists, resolves attributes directly or through `$ATTRIBUTE_LIST`, expands nonresident runlists, reads and writes plain nonresident attribute data through the buffer cache, decompresses compressed reads, performs directory lookup and directory enumeration, converts NTFS timestamps, and manages filename charset conversion.

Major metadata functions include `ntfs_loadntnode()`, `ntfs_attrtontvattr()`, `ntfs_runtovrun()`, `ntfs_ntvattrget()`, `ntfs_findvattr()`, `ntfs_ntlookup()`, `ntfs_ntget()`, `ntfs_ntput()`, `ntfs_ntref()`, `ntfs_ntrele()`, `ntfs_fget()`, and `ntfs_frele()`.

Directory logic is split between `ntfs_ntlookupfile()` and `ntfs_ntreaddir()`. Lookup scans `$INDEX_ROOT:$I30`, optionally follows index-allocation subnodes, handles `filename:stream` syntax through attribute definition lookup, and instantiates target vnodes via `ntfs_vgetex()`. Readdir fakes a flat stream over NTFS directory indexes by reading `$INDEX_ROOT`, `$BITMAP:$I30`, and `$INDEX_ALLOCATION:$I30`.

Data I/O is handled by `ntfs_readattr()`, `ntfs_readattr_plain()`, `ntfs_readntvattr_plain()`, `ntfs_writeattr_plain()`, and `ntfs_writentvattr_plain()`. Reads support resident data, nonresident runlists, sparse holes, and compressed units. Writes are limited to plain nonresident attributes and cannot extend files.

Other support includes `ntfs_procfixups()` for NTFS update-sequence fixups, `ntfs_toupper_use()` for loading `$UpCase`, `ntfs_u28()`/`ntfs_82u()` and init/uninit helpers for Unicode/local charset conversion, and string comparison helpers used by case-sensitive/case-insensitive lookup.

Research notes: the code contains old/disabled helper functions under `#if 0`. Several comments flag imperfect locking or old assumptions. The implementation is functional but conservative: no create/delete path is present here, and write support is constrained.
