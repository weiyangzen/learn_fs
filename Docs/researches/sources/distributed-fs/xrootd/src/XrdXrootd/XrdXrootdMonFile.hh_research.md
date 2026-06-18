# sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdMonFile.hh

Purpose: declares the static file-stat monitoring producer for the XRootD monitor `"f"` stream.

Important APIs/types/functions: public static `Close`, `Defaults`, `Disc`, `Init`, and `Open`; scheduled `DoIt`; private static `DoXFR`, `Flush`, and `GetSlot`. Static data covers buffer locks, file-map locks, active-file maps, report buffer pointers, record counters, report interval, transfer interval, buffer size, preformatted transfer/close records, and option flags.

Control flow: external file events call `Open`, `Close`, and `Disc`; the scheduler calls `DoIt` for periodic transfer snapshots and flushing.

State and persistence behavior: process-global static state only. It mirrors currently open monitored files and accumulated packet contents until flushed to collectors.

Dependencies: `XrdJob`, `XrdSysPthread`, `XrdXrootdMonFMap`, `XrdXrootdMonitor`, and forward declarations for file stats and monitor packet structures.

Integration points: friend-accessed from `XrdXrootdMonitor`; called by xrootd file handling code that updates `XrdXrootdFileStats`.

Risks: static global state makes test isolation and reconfiguration difficult. Consumers must call `Defaults()` before `Init()` so sizes/options are coherent. Lock ordering between file-map and buffer locks must remain consistent to avoid stalls.

Test signals: static initialization order, reinitialization attempts, scheduler lifecycle, fstat option combinations, and multi-threaded open/close/XFR stress.
