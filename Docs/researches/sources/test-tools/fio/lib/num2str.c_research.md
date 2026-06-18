# sources/test-tools/fio/lib/num2str.c

Purpose: converts numeric quantities to human-readable strings with SI/IEC prefixes and units.

Important APIs/functions: `bytes2str_simple` writes a two-decimal IEC byte string into a caller buffer; `num2str` returns a malloc-owned compact string constrained by a maximum numeric length and unit type.

Control flow: `bytes2str_simple` repeatedly divides by 1024 and formats `"%.2f %sB"`. `num2str` chooses SI or IEC prefixes, optionally converts bytes to bits, adjusts the starting prefix from `base`, divides until the integer part fits `maxlen`, applies carry rounding, and formats with `asprintf`.

State/persistence: no global mutable state. `num2str` allocates and transfers ownership to the caller; `bytes2str_simple` uses caller storage.

Dependencies/integration: uses fio `asprintf`, compile-time assertions, and `num2str.h` units. Used in human-readable status/stat output.

Risks/test signals: comments acknowledge rounding imprecision. Multiplying by 8 for bit units can overflow `uint64_t`. Tests should cover exact boundaries around 1000/1024, carry rounding, all unit modes, and allocation failure behavior.
