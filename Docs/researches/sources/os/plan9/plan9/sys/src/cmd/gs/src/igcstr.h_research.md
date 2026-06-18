# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/igcstr.h

Declares internal string GC APIs.

Key points:
- Declares `gc_locate` from `ilocate.c`.
- Declares string GC functions exported by `igcstr.c`: mark setup, single-string marking, relocation clearing/setting, compaction, and mutable/const/parameter string relocation helpers.

Research relevance:
- Internal interface between the main object GC and string-specific compaction.
