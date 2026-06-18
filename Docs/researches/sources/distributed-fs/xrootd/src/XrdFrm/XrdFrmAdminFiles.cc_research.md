<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdFrm/XrdFrmAdminFiles.cc -->
# sources/distributed-fs/xrootd/src/XrdFrm/XrdFrmAdminFiles.cc

## Purpose
`XrdFrmAdminFiles.cc` implements admin operations that mark files migratable/purgeable, set or clear mmap attributes, set or clear pin attributes, and retain obsolete lock/pin sidecar-file compatibility routines.

## Important Functions
`ckAttr()` maps an LFN to PFN, stats it, and decides whether a single file or whole directory should be processed, prompting for directory-wide operations when needed. `mkMark()` sets copy-time metadata with `XrdFrcUtils::updtCpy()`. `mkMmap()` writes or deletes `XrdFrm.Mem` xattrs using flags derived from `-keep`, `-lock`, and `-off` option state. `mkPin()` writes or deletes `XrdFrm.Pin` xattrs using permanent, idle, or until-time semantics. Obsolete `mkFile()`, `mkLock()`, and `mkStat()` create sidecar `.lock` or `.pin` files with ownership and timestamp semantics.

## Control Flow, State, And Persistence
Commands process either a single PFN or a directory tree through `XrdFrmFiles`, respecting `-recursive` and `/*`. Persistent state is xattrs for modern metadata and sidecar lock/pin files for backward compatibility. Counters update `numFiles`; failures set `finalRC`.

## Dependencies And Integration Points
The file uses `XrdFrmConfig::LocalPath`, `XrdFrmFiles`, `XrdFrcUtils`, and `XrdOucXAttr` over the xattr payload classes. It depends on option parsing performed in `XrdFrmAdmin.cc` and keep-time parsing for pin behavior.

## Risks And Test Signals
The option mapping in `Mmap()` from `XrdFrmAdmin.cc` uses `lock` as option code `f` and `off` as `l`, which then arrive in generic `Opt.Fix` and `Opt.Local`; this is hard to reason about and should be covered by CLI tests. Directory prompts are safety-critical. The obsolete `mkFile()` uses fixed buffers and temporary rename logic; if still reachable via `makelf`, it needs filesystem permission, ownership, timestamp, and cleanup tests. Xattr tests should validate mmap flag combinations, pin removal when no keep is supplied, recursive traversal, and error propagation from `XrdFrmFiles`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdFrm/XrdFrmAdminFiles.cc -->
