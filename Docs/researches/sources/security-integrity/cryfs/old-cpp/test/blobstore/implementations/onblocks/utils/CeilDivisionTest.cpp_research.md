# sources/security-integrity/cryfs/old-cpp/test/blobstore/implementations/onblocks/utils/CeilDivisionTest.cpp

Purpose: unit tests for `ceilDivision` math helper.

Important APIs/types/functions: `CeilDivisionTest`, `ceilDivision`, and 64-bit integer constants.

Control flow: checks divisions by 4, 1, 2, equal operands, and a 64-bit value larger than `uint32_t::max`.

State and persistence behavior: pure function tests with no state.

Dependencies and integration points: includes `blobstore/implementations/onblocks/utils/Math.h`, GoogleTest, and `<limits>`. The helper is used by blob/data tree sizing logic.

Risks and test signals: good boundary coverage for exact and non-exact division. Does not cover division by zero, which should either be disallowed by contract or asserted elsewhere.
