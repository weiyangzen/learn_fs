# File Research: sources/os/plan9/plan9/sys/src/cmd/5c/peep.c

## Scope

ARM backend peephole optimizer for the Plan 9 C compiler (`5c`). It operates after register-flow construction and before final object emission.

## Behavior

- Completes missing `Reg` nodes for non-pseudo instructions in the program stream.
- Repeatedly applies copy propagation, constant propagation, register substitution, and shift folding into ARM shifter operands.
- Rewrites simple instruction patterns, including `EOR $-1,x,y` to `MVN x,y`, duplicate byte/halfword moves, zero compare elimination, and indexed addressing transformations.
- Converts eligible short branch diamonds into predicated ARM instructions via `predicate()`.
- Uses `copyu()`, `copyas()`, `copyau()`, and substitution helpers to classify register use/set behavior across many ARM opcodes.

## Dependencies

Depends on `gc.h`, compiler globals (`firstr`, `zprog`, `debug`), ARM opcode/address enums, and register-flow structures from `reg.c`.

## Risks And Invariants

- Optimization correctness depends on precise single-predecessor/single-successor analysis; ambiguous branches, merges, and calls intentionally stop transformations.
- `copyu()` treats unknown opcodes conservatively as read-alter-write, which protects correctness but limits optimization.
- Predication assumes 5l encoding behavior for CPSR modification and caps predicated chains at four non-NOP instructions.
- Indexed-address rewriting must preserve base-register liveness; helper checks are local and conservative.
