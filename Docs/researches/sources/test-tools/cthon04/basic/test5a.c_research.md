# sources/test-tools/cthon04/basic/test5a.c

Purpose: write-focused large-file test with a read-back integrity check.

Important APIs/types/functions: same option model as test5, including optional -s for O_SYNC. Uses open()/creat(), write(), stat(), read(), optional mmap/msync, timing helpers, and complete().

Control flow: writes the target bigfile count times, verifying zero size after create/truncate and expected final size after close. It then opens the final file once and checks the integer pattern.

State and persistence: creates or overwrites bigfile and leaves it in the test directory for a later read-only test such as test5b.

Dependencies and integration points: complements test5b; both use the same BUFSZ/DSIZE defaults and tests.h DCOUNT.

Risks: leaves generated data behind by design; very large size/count values stress disk quota and cache behavior; pattern validation has the same partial-int limitation as test5.

Test signals: failure on create/write/close/stat/read mismatch; success reports bytes written and optional throughput, then complete().
