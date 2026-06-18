## sources/distributed-fs/xrootd/src/XrdFrm/XrdFrmPurge.hh

Purpose: declares the process-global purge policy manager and per-space policy object. It is the core API for configuring purge thresholds and running purge cycles from `frm_purge`.

Important APIs/types: public static methods include `Display()`, `Init()`, `Policy()`, and `Purge()`. Private helpers manage candidate addition, deferred queue advancement, eligibility, low-space detection, namespace scanning, stats, deletion, verbose tracking, and external policy checks. Per-object fields hold space stats, min/max free thresholds, hold intervals, external policy flag, counters, stop/enabled state, an `XrdFrmTSort`, and fixed-size deferred queues.

State and persistence: static `First`/`Default` form the policy list, `PolProg`/`PolStream` encapsulate an external program, and reset timers coordinate rescans. Persistent effects happen in the `.cc` implementation through OSS/CNS/CMS operations.

Dependencies and integration: includes `XrdFrmTSort.hh` and `XrdOssSpace.hh`, and forward declares filesets, policy program, streams, and `XrdOucTList`. `XrdFrmPurgMain.cc` owns setup, while purge implementation owns execution.

Risks and test signals: fixed `DeferQsz` buckets and process-global static state make behavior sensitive to long-running daemon lifetimes. Tests should validate policy replacement, default policy discovery, destructor `Clear()` deletion of deferred/candidate filesets, and one-time override application.
