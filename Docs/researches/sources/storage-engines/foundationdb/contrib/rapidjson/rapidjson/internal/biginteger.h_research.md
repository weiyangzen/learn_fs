# sources/storage-engines/foundationdb/contrib/rapidjson/rapidjson/internal/biginteger.h

Purpose: `internal::BigInteger` is a fixed-capacity unsigned big integer used by precise decimal-to-double conversion in `strtod.h`.

Important APIs and types: The class stores 64-bit `Type` digits in little-endian order with fixed `kCapacity`. It supports construction from `uint64_t` or decimal character spans, copy/assignment, addition by `uint64_t`, multiplication by `uint64_t` or `uint32_t`, left shift, equality, `MultiplyPow5`, `Difference`, `Compare`, `GetCount`, `GetDigit`, and `IsZero`.

Control flow: Decimal construction parses chunks up to 19 digits, repeatedly multiplying the current value by `10^chunkLength` using `MultiplyPow5(exp) <<= exp`, then adding the parsed chunk. Multiplication uses platform intrinsics or `unsigned __int128` when available, with a manual 32-bit split fallback. Difference orders operands, subtracts with borrow, and returns whether the original value was smaller than the RHS.

State and persistence behavior: State is the in-object digit array and count. There is no heap allocation or persistence. The capacity is sized for decimal conversion workloads rather than arbitrary unbounded arithmetic.

Dependencies and integration points: It depends on `rapidjson.h` and optional MSVC x64 intrinsics. `strtod.h` uses it to compare an approximated double against the exact scaled decimal within half an ULP.

Risks: Capacity assertions protect expected parse ranges but are not recoverable in release builds if assumptions are violated. Shift and multiplication code is architecture-sensitive. `Difference()` assumes unequal operands and writes only significant digits, so callers must initialize/interpret output carefully.

Test signals: Cover decimal parsing across chunk boundaries, multiplication by 0/1/large values, powers of five, left shifts by word and non-word bit counts, comparison ordering, exact differences, and fallback multiplication on non-x64 builds.
