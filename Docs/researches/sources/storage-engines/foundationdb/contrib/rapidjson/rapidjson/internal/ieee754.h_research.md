# sources/storage-engines/foundationdb/contrib/rapidjson/rapidjson/internal/ieee754.h

Purpose: `internal::Double` wraps IEEE-754 binary64 bit inspection and small helper operations used by RapidJSON number parsing and formatting.

Important APIs and types: Constructors accept `double` or raw `uint64_t`. Methods include `Value()`, `Uint64Value()`, `NextPositiveDouble()`, `Sign()`, `Significand()`, `Exponent()`, `IsNan()`, `IsInf()`, `IsNanOrInf()`, `IsNormal()`, `IsZero()`, `IntegerSignificand()`, `IntegerExponent()`, `ToBias()`, and static `EffectiveSignificandSize(int order)`.

Control flow: Methods mask and shift the raw `uint64_t` representation. Normal values include the hidden significand bit; denormal values use the denormal exponent path. `NextPositiveDouble()` increments the raw representation and asserts the value is non-negative.

State and persistence behavior: State is a union of `double` and `uint64_t` in the wrapper object. There is no external state or persistence.

Dependencies and integration points: It depends on `rapidjson.h` for constants and assertions. `dtoa.h` uses it for zero/sign detection, while `strtod.h` uses integer significands, exponents, ULP comparison, and next-double adjustment.

Risks: The implementation assumes IEEE-754 binary64 layout and compatible union type punning. `IsNormal()` treats zero as normal for hidden-bit decisions through `Significand() == 0`, matching this code's needs but not the strict mathematical definition. `NextPositiveDouble()` is only valid for positive finite ranges.

Test signals: Verify bit decoding for zero, negative zero, normal, denormal, infinity, and NaN; `IntegerExponent()` around denormal boundaries; `EffectiveSignificandSize()` for underflow and normal orders; and `ToBias()` ordering behavior.
