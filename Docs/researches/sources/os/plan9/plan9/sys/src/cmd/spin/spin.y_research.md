# File Research: sources/os/plan9/plan9/sys/src/cmd/spin/spin.y

This is the Yacc grammar for Promela plus embedded LTL syntax. It constructs `Lextok`, `Sequence`, and process definitions used by the rest of Spin.

Parser globals:
- `Mpars`: max message parameters.
- `nclaims`: number of never claims.
- `ltl_mode`: lexer/parser mode for LTL formulas.
- `Expand_Ok`, `realread`, `IArgs`, `NamesNotAdded`, `in_for`: parsing context flags.
- `claimproc` and `eventmap`: selected/current claim and trace names.
- Internal flags track embedded struct references, event-map parsing, and initialized declarations.

Top-level grammar:
- `program` is a sequence of units.
- Units include proctypes, init, never claims, LTL formulae, event traces, declarations, typedefs, C code fragments, inline definitions, semicolons, and errors.
- `proc` registers active or passive proctypes through `ready()` and may instantiate active ones through `runnable()`.
- `init` registers and starts the init process.
- `claim` increments `nclaims` and registers a never claim.
- `events` registers trace or notrace bodies.

Statement support:
- Declarations with visibility modifiers: `hidden`, `show`, `local`.
- Channel initializers update synchronous/asynchronous channel counts and message-field maximums.
- Send/receive forms include normal, sorted, random, poll, and random-poll variants.
- Control constructs include `if`, `do`, `for`, `select`, `break`, `goto`, labels, `unless`, `atomic`, `d_step`, and plain non-atomic blocks.
- Inline invocations are expanded by `pickup_inline()`.
- C fragments and C expressions are captured as pseudo-inlines.
- Assignments and increments/decrements perform tracking and reject channel arithmetic.

Expression support:
- Arithmetic, bitwise, comparison, boolean, shifts, conditional expression, `run`, `len`, `enabled`, channel probes, remote label/variable refs, `timeout`, `np_`, `pc_value`, and LTL operators.
- LTL includes `U`, release, weak-until expansion, implies, equivalence, next, always, and eventually.

Post-grammar helpers:
- `recursive()` renders a parsed LTL AST back to a textual formula.
- `ltl_to_string()` writes the formula through a temporary file and stores it as a string symbol for later translation.
- `yyerror()` delegates to `non_fatal()`.

Risk notes:
- The grammar deliberately uses many semantic actions, so parsing has side effects on symbol tables, process lists, code fragments, and analysis flags.
- LTL conversion writes `_S_p_I_n_.tmp`, then unlinks it; concurrent invocations in the same directory would collide.
