<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/print_fields.h -->
# sources/test-tools/strace/src/print_fields.h

Purpose: shared inline output primitives and field/value macros used throughout strace and some tests.

Important APIs/types/functions: `tprint_struct_*`, `tprint_array_*`, `tprints_arg_*`, `tprint_comment_*`, `tprint_indirect_*`, `tprint_value_changed`, `tprint_unavailable`, `PRINT_VAL_*`, and many `PRINT_FIELD_*` macros.

Control flow: inline helpers emit punctuation, color sequences when `IN_STRACE` is defined, argument names when `Nflag` is enabled, and formatted scalar/field values. In non-strace test builds, macros map to stdio and no-op color constants.

State and persistence behavior: no owned state, but behavior depends on global formatting state such as color enablement, `Nflag`, and xlat verbosity through callers.

Dependencies and integration points: included by `defs.h` consumers across the decoder tree; bridges production strace output and test helper builds.

Risks: tiny punctuation/color changes affect golden output broadly. Macros evaluate arguments in C macro contexts, so callers must avoid side effects where a macro may reference fields multiple times.

Test signals: broad decoder golden tests, color/no-color output, named-argument mode, non-strace test compilation, and field macro coverage for signed, unsigned, hex, arrays, pointers, flags, and comments.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/print_fields.h -->
