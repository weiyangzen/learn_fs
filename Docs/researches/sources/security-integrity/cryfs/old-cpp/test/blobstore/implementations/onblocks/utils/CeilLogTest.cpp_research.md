# sources/security-integrity/cryfs/old-cpp/test/blobstore/implementations/onblocks/utils/CeilLogTest.cpp

Purpose: unit tests for `ceilLog` math helper.

Important APIs/types/functions: `CeilLogTest`, `ceilLog`, and 64-bit value checks.

Control flow: verifies base-3 logs around powers and non-powers, plus base-1024 log for a 1 TiB value.

State and persistence behavior: pure function tests with no state.

Dependencies and integration points: includes `Math.h`, GoogleTest, and `<limits>`. Used by tree-depth or layout calculations.

Risks and test signals: confirms representative small and 64-bit cases. TODO indicates broader cases are still needed; invalid bases and zero values are not covered.
