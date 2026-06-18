# sources/security-integrity/cryfs/old-cpp/test/blobstore/implementations/onblocks/utils/IntPowTest.cpp

Purpose: unit tests for integer exponentiation helper `intPow`.

Important APIs/types/functions: `IntPowTest`, `intPow`, and 64-bit power case.

Control flow: covers zero exponent, zero base, exponent one, powers of two and ten, arbitrary bases, and a 64-bit base cubed.

State and persistence behavior: pure function tests with no state.

Dependencies and integration points: includes blobstore math helper and GoogleTest. Math results feed blob/data-tree layout sizing.

Risks and test signals: broad normal-case coverage. It does not test overflow behavior, so callers must avoid values that exceed the return type.
