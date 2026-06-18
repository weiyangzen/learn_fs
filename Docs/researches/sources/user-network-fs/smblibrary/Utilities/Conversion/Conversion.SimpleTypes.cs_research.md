# sources/user-network-fs/smblibrary/Utilities/Conversion/Conversion.SimpleTypes.cs

Purpose: this partial `Conversion` class provides forgiving object-to-simple-type conversion helpers with default values.

Important APIs/types/functions: `ToInt16`, `ToInt32`, `ToInt64`, `ToUInt16`, `ToUInt32`, `ToUInt64`, `ToFloat`, `ToDouble`, `ToDecimal`, `ToBoolean`, `ToString`, `ToChar`, and `ToDateTime`, most with overloads accepting a default value.

Control flow: each method initializes a result to the default, checks for null, calls the matching `System.Convert` method inside a broad `try/catch`, and silently returns the default on any exception.

State and persistence behavior: stateless.

Dependencies and integration points: likely used by UI/config parsing code that prefers defaults over exceptions.

Risks: catching all exceptions hides format, overflow, culture, and invalid-cast errors. `ToString(object)` has no caller-supplied default overload and returns empty string for null/failure. Culture-sensitive conversions may vary by current culture.

Test signals: tests should cover nulls, invalid strings, overflows, culture-sensitive decimal/date inputs, and explicit nonzero defaults.
