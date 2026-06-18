## sources/object-store/apache-ozone/hadoop-ozone/cli-repair/src/main/java/org/apache/hadoop/ozone/repair/om/OMRatisLogRepair.java

Purpose: offline OM Ratis log surgery command that replaces one failing OM transaction at a given Raft index with an `EchoRPC` no-op request.

Important APIs and control flow: `--index` and `--backup` are required. The mutually exclusive argument group accepts either `--segment-path` or `--ratis-log-dir`; directory mode finds the matching `log_<start>-<end>` or `log_inprogress_<start>` file. `execute` validates the segment path, prevents backup in the segment directory, creates a backup copy, streams the segment with `LogSegment.readSegmentFile`, and writes every entry to a temp output segment. `processLogEntry` leaves other entries unchanged and calls `getOmEchoLogEntry` for the target index, preserving Raft metadata while replacing OM request bytes. The temp segment atomically replaces the original.

State and dependencies: rewrites Ratis segment files and creates backups; uses Apache Ratis log APIs and OM request conversion helpers.

Risks and test signals: this is destructive and must be applied consistently across OMs only for the documented all-OM crash case. Dry-run still reads and validates but skips file mutation. No direct test in this subset.
