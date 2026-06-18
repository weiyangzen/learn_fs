# sources/test-tools/strace/src/strauss.h

Purpose: public interface for Strauss mascot and tip printing.

Important APIs/types/functions: `STRAUSS_START_VERBOSITY`, `enum tips_fmt` (`TIPS_NONE`, `TIPS_COMPACT`, `TIPS_FULL`), `enum tip_ids` (`TIP_ID_RANDOM`), `strauss_lines`, `show_tips`, `tip_id`, `print_strauss`, and `print_totd`.

Control flow: consumers set `show_tips`/`tip_id` during option parsing, pass version verbosity to `print_strauss`, and call `print_totd` at exit or when usage handling wants a tip.

State and persistence behavior: declares mutable process globals; no ownership or persistence beyond process lifetime.

Dependencies and integration points: included by `strace.c` and implemented by `strauss.c`; depends on `size_t` being available through existing include context.

Risks: header exposes globals rather than accessors, so future callers can create inconsistent tip state. Include ordering must provide `size_t`.

Test signals: compile with users of the header, parse `--tips` modes, and verify `-V` repetition increments art verbosity consistently.
