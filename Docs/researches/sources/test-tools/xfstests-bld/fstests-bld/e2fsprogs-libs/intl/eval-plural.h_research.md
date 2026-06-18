<!-- BEGIN_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/intl/eval-plural.h -->
# sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/intl/eval-plural.h

## Purpose
This header provides the recursive evaluator for parsed gettext plural expressions. It converts a `struct expression` tree and count `n` into a plural-form index.

## Important APIs, Types, and Functions
The key function is `plural_eval(struct expression *pexp, unsigned long int n)`, optionally declared `static` through `STATIC`. It operates on expression operations such as `var`, `num`, `lnot`, `lor`, `land`, arithmetic, comparisons, and ternary `qmop` from `plural-exp.h`.

## Control Flow
Evaluation dispatches by `pexp->nargs`: zero-argument nodes return `n` or numeric constants, one-argument nodes compute logical not, two-argument nodes short-circuit `||` and `&&` or evaluate arithmetic/comparison operations, and three-argument nodes implement the conditional operator. Division and modulo explicitly raise `SIGFPE` when configured for platforms where integer divide-by-zero does not.

## State and Persistence
There is no stored state. The evaluator is pure except for possible `SIGFPE` raising on divide/modulo by zero.

## Dependencies and Integration Points
It depends on the plural expression tree produced by gettext plural parsing/extraction and is included directly by `dcigettext.c` for `plural_lookup`.

## Risks
Deep or malformed expression trees can recurse heavily. Invalid operations fall through to return zero. Divide-by-zero behavior can terminate or signal the process. Bounds checking for the returned index is performed by `plural_lookup`, not this evaluator.

## Test Signals
Evaluate fixture expressions for common languages, ternary expressions, logical short-circuiting, arithmetic precedence from parsed trees, out-of-range values, and divide/modulo by zero behavior.
<!-- END_FILE_RESEARCH: sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/intl/eval-plural.h -->
