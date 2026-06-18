# File Research: sources/os/plan9/9front/sys/src/cmd/dtracy/type.c

This file performs dtracy expression type checking and optimization before bytecode generation or record capture. It adds casts to model C-like integer semantics, folds constants, decides which subexpressions must be recorded from the kernel, and removes unnecessary casts.

Key responsibilities:
- `typecheck` annotates expressions with `Type`, validates operations, and inserts integer casts.
- `evalop` implements constant/runtime binary operator semantics, including signed/unsigned division and shifts.
- `cfold` folds constant expressions and integer casts.
- `calcrecsize` estimates the minimal record bytes needed to reproduce a value in user space.
- `insrecord` wraps runtime-needed subexpressions in `ORECORD`.
- `elidecasts` tracks known data bits and upper-bit extension to remove redundant casts.
- `exprcheck` runs the whole pipeline and emits debug stages under `-d`.

Important implementation notes:
- The comment explicitly says it uses kencc, not ANSI C, unsigned semantics.
- `icast(int sign, int size, Node *n)` calls `type(TYPINT, sign, size)`, but every other call uses `type(TYPINT, size, sign)`. This looks like a real argument-order bug because `type` expects size first, sign second.
- `DTV_TIME` and `DTV_PROBE` are treated as record-free variables; other variables require record capture.
