# File Research: sources/local-fs/reiserfsprogs/fsck/info.c

Contains user interaction and stage reporting helpers.

Functions:
- `fsck_user_confirmed(fs, q, a, default_answer)`: asks only in interactive mode; otherwise returns the supplied default.
- `stage_report(pass, fs)`: prints statistics for rebuild/check stages and then clears the rebuild stats union.

Reported stages:
- Pass 0: scanned blocks, leaves, corrected/skipped leaves, wrong pointers, objectids.
- Pass 1: leaves read/inserted, metadata pointers zeroed, saved items, uninsertable leaves, non-unique pointers.
- Pass 2: item-by-item inserted leaves, shared objectids, relocated/rewritten files.
- Semantic pass: files, directories, symlinks, broken files, fixed sizes, deleted names, objectid sharing.
- Lost+found pass: recovered/lost objects, linked dirs/files, relocated objectid-sharing objects.
- Pass 4: deleted unreachable items.
- Final check stats: leaves, internals, dirs, files, data pointers, zero pointers, safe links.

Key role: centralized human-readable fsck progress summaries.
