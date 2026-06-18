# sources/test-tools/ltp/testcases/kernel/syscalls/sigtimedwait/Makefile

## Purpose
This Makefile is the leaf build description for the LTP syscall tests in `sigtimedwait`. It sets `top_srcdir`, includes LTP's common `testcases.mk`, and delegates normal target generation to `generic_leaf_target.mk`. It also carries local target-specific build policy: `LTPLDLIBS  = -lltpsigwait`.

## Important APIs, types, and functions
The important interfaces are GNU make variables and includes: `top_srcdir`, optional per-target `CFLAGS`/`CPPFLAGS`/`LDLIBS`/filter variables, `$(top_srcdir)/include/mk/testcases.mk`, and `$(top_srcdir)/include/mk/generic_leaf_target.mk`. These integrate the directory with the shared LTP build harness.

## Control flow
Make evaluates local variable assignments first, imports the shared testcase rules, then imports the generic leaf target rules that discover and build the local C test programs. Any target-specific flag line is applied only to the named binary before linking.

## State and persistence behavior
The file itself has no runtime state. Build state is produced by the inherited LTP make rules: object files, test binaries, and dependency artifacts under the configured build tree.

## Dependencies and integration points
It depends on the repository-level LTP make include hierarchy and on the C sources in the same syscall directory. It is the integration point that lets higher-level LTP builds compile and install these tests.

## Risks and edge cases
The main risk is that local flags or filters diverge from the C tests that need them. Missing `top_srcdir` or include files will break builds from nonstandard invocation paths.

## Test signals
A successful `make` in this directory, or a higher-level LTP build selecting this directory, should compile the listed syscall tests and apply any target-specific flags without linker errors.
