# File Research: sources/os/plan9/9front/sys/src/cmd/qc/machcap.c

Target capability filter for the Power backend. `machcap` tells the common compiler which operations this backend can lower directly.

Key responsibilities:
- Accepts 64-bit arithmetic/logical/shift support for selected operations.
- Accepts multiply and compound multiply in several cases.
- Accepts boolean, comparison, conditional, comma/list, logical, increment/decrement, and many compound assignment operations.
- Rejects division/modulo and compound division/modulo for direct target handling, forcing generic/runtime paths.
- Allows casts between vlong and non-floating types.

Dependencies and coupling:
- Uses common type predicates such as `typev`, `typefd`, `typechl`, and `mixedasop`.
- Influences earlier compiler lowering before `cgen.c`.

Notable behavior:
- Conservative around mixed compound assignments and floating/vlong casts.
