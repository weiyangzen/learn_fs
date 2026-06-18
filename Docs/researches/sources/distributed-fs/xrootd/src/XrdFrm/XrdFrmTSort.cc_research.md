## sources/distributed-fs/xrootd/src/XrdFrm/XrdFrmTSort.cc

Purpose: implements a lightweight age sorter for purge candidates. It returns filesets from oldest access time to newest, optionally ordering equally old entries by decreasing file size.

Important APIs and control flow: `Add()` rejects entries with future access time, computes `Age = baseT - st_atime`, and places the entry into a day bucket capped at 63. `Oldest()` walks the multi-level table from seconds to minutes to hours to days, lazily rebucketing lists with `Bin()` as it descends. `Bin()` extracts six-bit time fields and optionally calls `Insert()` at the seconds level when size sorting is enabled. `Purge()` deletes every remaining fileset and resets state.

State and persistence: all state is in memory: `FSTab[4][64]`, `baseT`, entry counts, and current highest non-empty bucket indexes. Fileset ownership transfers to the sorter until `Oldest()` returns it or `Purge()` deletes it.

Dependencies and integration: used by `XrdFrmPurge` as `FSTab` for eligible candidates. It depends on `XrdFrmFileset::baseFile()` stat data.

Risks and test signals: time bucketing is approximate and capped at 63 days for the day bucket. Future atimes are silently rejected. Tests should validate oldest-first ordering across bucket boundaries, size ordering only in final bucket, ownership deletion on purge, and behavior when `baseT` is fixed at reset while scans take time.
