# sources/test-tools/strace/src/scno.am

Purpose: Automake fragment that generates `scno.h`, a syscall-number header derived from preprocessed architecture syscall table entries.

Important APIs/types/functions: `SCNO_CPPFLAGS`, `syscallent.i` preprocessing rule, `SCNO_SED`, `scno.h` generation rule, `CLEANFILES`, and inclusion of `scno_hook.mk` through an `eval include` hidden from automake.

Control flow: make preprocesses `src/$(OS)/$(ARCH)/syscallent.h` with `config.h` and architecture flags into `syscallent.i`. The `scno.h` rule writes a generated-file banner, appends `scno.head`, runs a sed expression that ignores indirect subcall entries, extracts syscall numbers and names, and emits guarded `__NR_name` definitions with `SYSCALL_BIT`.

State and persistence behavior: produces build artifacts `syscallent.i` and `scno.h`, both registered as clean files. It writes through a temporary `$@-t` file and renames it into place.

Dependencies and integration points: depends on automake variables, C preprocessor, `src/scno.head`, arch syscall tables, and `scno_hook.mk` to add the build dependency from `Makefile` to `scno.h` for ordinary targets.

Risks: the sed expression is tightly coupled to syscall table initializer formatting. New table syntax, nonstandard syscall names, or indirect subcall markers can cause missing or malformed definitions.

Test signals: build on multiple architectures, verify regenerated `scno.h` contains expected `__NR_*` guards, and run `make clean` to confirm generated intermediates are removed.
