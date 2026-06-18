# File Research: sources/os/plan9/9front/sys/src/cmd/acid/dot.c

Complex-type field lookup, field access, and type declaration support for Acid.

Key responsibilities:
- Searches type field lists by tag, preferring shallower nesting depth.
- Implements `(expr).field` by evaluating an address, finding a matching field, and reading or returning the field address.
- Builds `Type` lists from parsed complex/member ASTs.
- Defines complex types with `defcomplex()`.
- Declares variables or frame locals as complex types with `decl()`.

Important behavior:
- Field format `a` propagates nested complex type metadata and returns an address value.
- Non-address fields are read through `indir(cormap, addr, fmt, r)`.
- Frame declarations attach `Frtype` metadata to function symbols for later `frame:local` lookup.

Dependencies:
- Uses evaluator `expr()`, memory indirection, type symbols, and AST nodes from parser.

Notable risks:
- Complex member lists are append-only on the symbol’s `lt`; redefining without clearing can accumulate fields.
- Field access requires integer addresses and an existing `comt` type annotation.
