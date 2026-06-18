# sources/test-tools/cthon04/basic/test7b.c

Purpose: hard-link correctness and timing variant.

Important APIs/types/functions: parses -h, -t, -f, -n plus files/count/fname/nname. Uses link(), stat(), unlink(), errno/EOPNOTSUPP, and DOS/Win32 rename fallback.

Control flow: for each generated file, creates a second directory entry with link(), verifies both names report link count 2, removes the new name, and verifies the original link count returns to 1. DOS/Win32 performs rename out/back and expects link count 1.

State and persistence: creates transient extra names and removes them each iteration; final cleanup removes original generated files.

Dependencies and integration points: complements test7a and test7 in harnesses that split rename/link behavior.

Risks: on filesystems that do not expose stable st_nlink, this can fail despite usable data access; unsupported hard links exit through complete() after EOPNOTSUPP.

Test signals: link-count checks are the main correctness signal; success reports link count and ok marker.
