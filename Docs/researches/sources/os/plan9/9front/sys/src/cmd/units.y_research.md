# File Research: sources/os/plan9/9front/sys/src/cmd/units.y

This yacc grammar implements the Plan 9 `units` converter. It reads `/lib/units` or a supplied database file, builds named unit definitions and fundamental dimensions, then enters an interactive “you have / you want” conversion loop.

`Node` stores a numeric value plus signed dimension exponents. The grammar supports unit definitions, fundamental dimension declarations with `#`, expressions with addition/subtraction for like units, multiplication/division, implicit multiplication, `|` division, integer exponents, and Unicode superscripts/multiply/divide characters.

The runtime includes unit lookup with metric prefix stripping and plural `s` stripping, special Celsius/Fahrenheit affine conversions, formatted dimension output, overflow/underflow-checked multiply/divide, and error-limited parsing diagnostics.
