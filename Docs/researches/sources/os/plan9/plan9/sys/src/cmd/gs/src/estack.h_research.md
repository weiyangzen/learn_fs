# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/estack.h

Interpreter execution-stack helper header.

Key points:
- Defines convenient access macros for the current interpreter context’s execution stack.
- Exposes cached current-file helpers: `esfile`, `esfile_clear_cache`, `esfile_set_cache`, `esfile_check_cache`.
- Documents Ghostscript’s execution stack model for procedures, control operators, and continuations.
- Defines e-stack mark and continuation operator macros:
  - `make_mark_estack`, `push_mark_estack`
  - `r_is_estack_mark`
  - `make_op_estack`, `push_op_estack`
- Provides stack capacity/underflow macros `check_estack` and `check_esp`.
- Defines mark types `es_other`, `es_show`, `es_for`, and `es_stopped`.
- Declares `pop_estack`.

Dependencies and interactions:
- Includes `iestack.h` and `icstate.h`.
- Used by interpreter operators that call out to PostScript procedures or need continuation state.
- Coupled to current-file lookup and e-stack block splitting invariants.

OS/filesystem relevance:
- Relevant to file execution indirectly because executable file refs on the execution stack feed `currentfile` behavior.
