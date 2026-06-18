# sources/distributed-fs/xrootd/src/XrdCks/XrdCksManOss.hh

Purpose: declares `XrdCksManOss`, an `XrdCksManager` specialization for storage systems exposed through the OSS plugin API. It is intended for internal checksum support where logical file names must be resolved by OSS rather than directly opened by POSIX calls.

Important APIs: virtual overrides for `Calc`, `Del`, `Get`, `List`, `Set`, and `Ver`, plus protected overrides of low-level `Calc` and `ModTime`. The constructor receives `XrdOss*`, error destination, I/O size, version info, and an autoload flag passed to the base class.

Control flow/state: the interface preserves the same checksum manager semantics while replacing path translation and file I/O. Persistent checksum state is still in extended attributes controlled by `XrdCksManager`. Dependencies include `XrdCksManager`, `XrdOss`, `XrdSysError`, and `XrdVersionInfo`. Risks are mostly integration risks: callers must pass LFNs to public methods, and the implementation must keep base-class PFN callbacks meaningful. Test signals: parity with POSIX manager behavior through OSS-backed files, stale mtime checks, and plugin autoload interaction.
