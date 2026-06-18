# File Research: sources/os/plan9/9front/sys/src/cmd/pc.y

## Role

Defines the grammar and implementation for an arbitrary-precision integer calculator.

## Number Model

`Num` embeds `mpint`, stores an output base hint, and uses reference counting. Copy-on-write helpers allow expression operations to mutate when uniquely owned and duplicate when shared.

Base selection can be weak or strong. Literals can use current input base or explicit binary/octal/decimal/hex prefixes. Output honors explicit output base or a number’s strong base.

## Grammar

The yacc grammar supports statements separated by newlines or semicolons, variable assignment, last-result access through `@`, base/control statements, numeric literals, symbols, function calls, unary operators, arithmetic, bitwise operators, comparisons, logical operators, exponentiation, shifts, conditional `?:`, and sign-extension via `$`.

Division/modulo semantics are controlled by `divmode`, with adjusted behavior for negative remainders in the default mode.

## Built-In Functions

Registered functions include base coercion (`hex`, `dec`, `oct`, `bin`, `pb`), numeric transforms (`abs`, `round`, `floor`, `ceil`, `trunc`, `xtend`), bit helpers (`clog`, `ubits`, `sbits`, `nsa`, `rev`, `cat`), number theory (`gcd`, `minv`), and random generation (`rand`).

## Lexer And UI

The lexer recognizes multi-character operators, numbers with underscores, identifiers including non-ASCII bytes, and prompts when stdin is `/dev/cons`.

`numprint` can emit digit group separators and optional bit-position headers for binary/octal/hex output.
