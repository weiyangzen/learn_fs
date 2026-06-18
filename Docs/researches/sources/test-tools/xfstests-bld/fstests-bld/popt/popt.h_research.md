# sources/test-tools/xfstests-bld/fstests-bld/popt/popt.h

Purpose: public API and ABI contract for the popt library. It defines option table syntax, argument types, modifier flags, error codes, context flags, alias/item structures, callback signatures, helper macros, and all exported parsing/config/help functions.

Important APIs/types: `struct poptOption`, `struct poptAlias`, `poptItem`, abstract `poptContext`, `poptCallbackType`, and `enum poptCallbackReason`. Key macros include `POPT_ARG_*`, `POPT_ARGFLAG_*`, `POPT_CBFLAG_*`, `POPT_ERROR_*`, `POPT_CONTEXT_*`, `POPT_AUTOHELP`, `POPT_AUTOALIAS`, and `POPT_TABLEEND`. Public functions include context lifecycle, parsing, config readers, argv parsing/duplication, help/usage, exec path, stripping, typed value savers, and `poptBits` operations.

Control flow: applications declare one or more `struct poptOption` arrays ending in `POPT_TABLEEND`, obtain a `poptContext`, then loop on `poptGetNextOpt`. Options with nonzero `val` can return control to the caller; options with `arg` pointers can be saved automatically. Included tables and callback rows affect recursive parsing and event handling.

State/persistence: the header exposes opaque context ownership rules and documents which arrays/strings are duplicated or retained. `poptItem` stores alias/exec metadata and argv arrays. `poptBits` is an allocated bitset whose storage is application-owned after use.

Dependencies/integration: includes `stdio.h` for `FILE *` and is consumed by all popt C files plus downstream programs. It carries Splint annotations, indicating long-standing ABI and static-analysis compatibility concerns.

Risks: flag values share bit fields, so callers must combine argument types and modifiers carefully. Some APIs return owned memory (`poptGetOptArg`, parse/dup helpers), while option-table strings are often borrowed; ownership mistakes can leak or double-free. Experimental flags such as `POPT_ARG_MAINCALL`, `POPT_ARG_BITSET`, `POPT_ARGFLAG_RANDOM`, and toggle/logical modifiers need targeted tests.

Test signals: `test1.c`, `test2.c`, `tdict.c`, and `testit.sh` collectively exercise most declared parser, config, help, numeric, argv, and bitset surfaces.
