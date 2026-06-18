# sources/distributed-fs/xrootd/src/XrdCks/XrdCksManager.cc

Purpose: implements the main checksum manager for local physical files. It registers checksum algorithms, computes file checksums, stores/retrieves them in extended attributes, validates staleness using file modification time, supports configured or autoloaded plugins, and verifies supplied checksums.

Important APIs: `Calc`, `Config`, `Init`, `Find`, `Del`, `Get`, `List`, `ModTime`, `Name`, `Object`, `Size`, `Set`, `SetOpts`, and `Ver`. Native calculators include `adler32`, `crc32`, `crc32c`, and `md5`; configured plugin calculators are initialized through `XrdCksCalcInit`; autoload uses `XrdCksLoader`.

Control flow/state: `csTab[8]` stores algorithm metadata, lengths, plugin handles, and ownership flags. `Calc` clones a calculator, mmap-reads the file in `segSize` windows, writes `XrdCksXAttr` when requested, and records `fmTime/csTime`. `Get` maps missing xattrs to `-ESRCH` and stale metadata to `-ESTALE`; `Ver` recalculates stale/missing attributes before comparing. Dependencies are POSIX file APIs, `XrdOucXAttr`, `XrdSysFAttr`, plugin loader utilities, and calculators. Risks: fixed capacity, mmap platform flags, shared global `CksOpts`, plugin trust, and mtime-only freshness. Test signals: config parsing, plugin failures, stale xattr detection, list filtering, default checksum swapping, and mmap error paths.
