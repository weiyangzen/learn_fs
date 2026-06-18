# sources/test-tools/fio/parse.h

Purpose: public option parser model and API declarations.

Important APIs/types: defines `enum fio_opt_type`, `struct value_pair`, `PARSE_MAX_VP`, `struct fio_option`, parser/exported helper declarations, callback typedefs, `td_var()`, percentage/zone encoding helpers, `ZONE_BASE_VAL`, and `struct print_option`.

Control flow and state: no parser implementation, but `td_var()` is the key storage helper: it chooses profile option storage when `o->prof_opts` is set, otherwise the thread option object, then applies the option offset.

Dependencies and integration: includes `<inttypes.h>` and `flist.h`; used by global options, profiles, and command-line/job-file parsing.

Risks: `struct fio_option` offsets are raw byte offsets into caller structs, so metadata mistakes are memory-safety bugs. Percent/zone encodings use unsigned wraparound, requiring callers to use helper predicates rather than direct comparisons.

Test signals: compile all option table definitions with `options_init()` diagnostics enabled and parser tests that validate offsets and encoded special values.
