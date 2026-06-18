# sources/test-tools/cthon04/basic/test7.c

Purpose: combined rename and hard-link correctness test.

Important APIs/types/functions: parses -h, -t, -f, -n plus files/count/fname/nname. Uses rename(), stat(), link(), unlink(), errno/EOPNOTSUPP handling, dirtree(), rmdirtree().

Control flow: creates files, then for each pass renames each original to a new name, verifies original disappearance and new existence. On Unix-like clients it links new back to original, checks link counts at 2, unlinks new, and checks original count returns to 1. On DOS/Win32 it renames back instead.

State and persistence: mutates generated filenames heavily and cleans up with rmdirtree(ignore=1) after the timed section.

Dependencies and integration points: tests link support where available; treats EOPNOTSUPP as unsupported and exits through complete() after reporting the attempted failure.

Risks: link count semantics vary on some network or pseudo filesystems; DOS/Win32 path is a rename fallback, not a hard-link test.

Test signals: stat/link-count mismatches or rename/link/unlink failures are fatal; success reports operation count and ok marker.
