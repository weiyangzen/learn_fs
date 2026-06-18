# sources/security-integrity/cryfs/old-cpp/test/blobstore/implementations/onblocks/utils/MaxZeroSubtractionTest.cpp

Purpose: unit tests for saturating subtraction helper `maxZeroSubtraction`.

Important APIs/types/functions: `MaxZeroSubtractionTest`, `maxZeroSubtraction`, `numeric_limits<uint32_t>::max`, and 64-bit cases.

Control flow: verifies equal operands return zero, positive differences are preserved, negative differences saturate at zero, subtraction from zero stays zero, and 64-bit values work.

State and persistence behavior: pure function tests with no state.

Dependencies and integration points: includes blobstore `Math.h`, GoogleTest, and `<limits>`.

Risks and test signals: strong edge coverage around unsigned underflow prevention. Overflow in the input expressions themselves is not explored.
