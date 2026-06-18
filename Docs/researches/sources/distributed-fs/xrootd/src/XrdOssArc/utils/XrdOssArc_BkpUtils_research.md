# sources/distributed-fs/xrootd/src/XrdOssArc/utils/XrdOssArc_BkpUtils

Purpose: Python Rucio helper for archive backup orchestration. It manages metadata keys, lists closed datasets needing backup, creates symlink arenas and optional manifests, reports DID stat data, resolves which archive contains a file, and marks backup completion.

Important APIs/functions: commands include `addkey`, `list`, `qkey`, `set`, `setup`, `finish`, `stat`, and `which`. `Get_lfns()` lists and sorts dataset files, optionally preserving checksums named by `XRDOSSARC_CKSUM`. `Get_lfn2pfn()` resolves PFNs for an RSE in batches controlled by `XRDOSSARC_MAXITEMS`. `Setup()` cleans/recreates the arena, creates `~n` symlink trees via `arcSymlink()`, optionally writes a manifest, splits archives according to `XRDOSSARC_SIZE` through `arcSplit()`, and prints total files/bytes. `Which()` uses `arcIndex` metadata to map a file ordinal to an archive name. `Stat()` emits CGI-style mode/uid/gid/size/time attributes.

State/persistence: mutates Rucio metadata (`arcBackup`, `arcIndex`, configured finish key), writes arena symlinks, optional manifest files, and removes arenas on finish. It depends on Rucio clients and local filesystem reachability of PFNs.

Risks/integration: several error paths appear malformed, including `Set_Backup("arcBackup",...)` called with the wrong shape in one branch and formatting chained after `Emsg()` calls; `xeq_Finish()` removal is nested under debug logging, so non-debug cleanup may be skipped. Tests should mock Rucio clients for metadata and replica batching, verify split ordinal math, ensure arena cleanup, and exercise malformed environment values and missing PFNs.
