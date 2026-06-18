# sources/security-integrity/cryfs/old-cpp/test/gitversion/VersionCompareTest.cpp

Purpose: unit tests ordering semantics for `gitversion::VersionCompare::isOlderThan`.

Important APIs/functions: fixture helpers `EXPECT_IS_OLDER_THAN` and `EXPECT_IS_SAME_AGE` assert both directions for asymmetric and equal-age comparisons.

Control flow: cases cover numeric version ordering, missing components treated as zero, zero prefixes, tag ordering (`alpha`, `beta`, `rc`, release), milestone-like tags, and dev suffix ordering by commit count while ignoring commit id differences at same count.

State/persistence: no persistent state.

Dependencies/integration: includes gtest and `gitversion/VersionCompare.h`; indirectly relies on parser behavior.

Risks: tag precedence is encoded by examples rather than a table, so new tags may need explicit tests. Dirty markers are treated as same age when commit count matches.

Test signals: CTest runs these through `gitversion-test`.
