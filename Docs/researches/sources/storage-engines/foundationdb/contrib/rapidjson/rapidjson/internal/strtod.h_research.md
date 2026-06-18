# sources/storage-engines/foundationdb/contrib/rapidjson/rapidjson/internal/strtod.h

Purpose: This header implements RapidJSON's internal decimal-to-double conversion, combining fast paths, DiyFp approximation, and BigInteger correction for full precision.

Important APIs and functions: Key functions are `FastPath`, `StrtodNormalPrecision`, `Min3`, `CheckWithinHalfULP`, `StrtodFast`, `StrtodDiyFp`, `StrtodBigInteger`, and `StrtodFullPrecision`. Inputs are parsed decimal digits, their length, decimal position, and exponent from the reader's number parser.

Control flow: Normal precision multiplies or divides by powers of ten with underflow splitting. Full precision first tries the exact fast path for small exponents/significands, trims leading and trailing zeros, limits extremely long digit sequences, checks underflow, then uses `DiyFp` cached powers to approximate. If the approximation is not provably outside the uncertain half-ULP band, `BigInteger` compares the exact scaled decimal against the candidate double and adjusts to the next positive double if needed.

State and persistence behavior: No persistent state. Temporary `BigInteger`, `DiyFp`, and `Double` values hold conversion state on the stack.

Dependencies and integration points: It depends on `ieee754.h`, `biginteger.h`, `diyfp.h`, and `pow10.h`. Reader number parsing feeds it and then stores results in DOM values or SAX events.

Risks: Decimal-position/exponent arithmetic is subtle, especially after zero trimming. The 780-digit cap and underflow check affect extreme inputs. Rounding-to-even and half-ULP comparison are correctness-critical. Negative values are handled by callers, so this code assumes non-negative significands in full precision.

Test signals: Cover fast-path exact integers, disguised fast paths, long decimals, leading/trailing zeros, subnormal underflow, overflow handled by reader, halfway round-to-even cases, next-double adjustment, and consistency against standard `strtod` on representative inputs.
