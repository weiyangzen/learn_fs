# sources/storage-engines/foundationdb/contrib/rapidjson/rapidjson/internal/dtoa.h

Purpose: This header provides RapidJSON's internal double-to-ASCII conversion using the Grisu2 algorithm plus formatting prettification.

Important APIs and functions: Core functions are `GrisuRound`, `CountDecimalDigit32`, `DigitGen`, `Grisu2`, `WriteExponent`, `Prettify`, and `dtoa(double, char*, int maxDecimalPlaces = 324)`. It uses `DiyFp`, cached powers, `Double` from `ieee754.h`, and `GetDigitsLut()` from `itoa.h`.

Control flow: `dtoa()` handles signed zero specially, emits a leading minus for negative finite values, runs `Grisu2()` to generate shortest significant digits and decimal exponent, then `Prettify()` chooses fixed or scientific notation. `DigitGen()` emits integral digits first, then fractional digits while tracking the safe rounding interval; `GrisuRound()` adjusts the last digit if the generated value is closer after decrementing.

State and persistence behavior: No persistent state exists. The caller owns the output buffer and receives a returned end pointer. Formatting mutates the buffer in place using `memmove` and appended punctuation/exponent bytes.

Dependencies and integration points: `Writer::WriteDouble()` relies on this output. The code depends on finite input handling by callers or writer policy. Integer digit LUT and cached power tables are performance-critical dependencies.

Risks: Buffer sizing is caller responsibility. `maxDecimalPlaces` truncates fixed decimal forms and can intentionally produce rounded-down display. NaN/Inf are not formatted here. Edge cases around negative zero, exponent thresholds, halfway values, and mantissa overflow are regression-sensitive.

Test signals: Cover zero and negative zero, smallest/largest normal and denormal finite doubles, powers of ten, halfway rounding cases, fixed-versus-exponent threshold transitions, `maxDecimalPlaces` truncation, and JSON writer integration for non-finite handling policy.
