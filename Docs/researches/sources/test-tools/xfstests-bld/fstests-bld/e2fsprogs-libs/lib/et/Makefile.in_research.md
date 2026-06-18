# sources/test-tools/xfstests-bld/fstests-bld/e2fsprogs-libs/lib/et/Makefile.in

## Purpose
`lib/et/Makefile.in` builds, installs, and tests the MIT com_err compatibility library and `compile_et` generator.

## Important APIs, Types, and Functions
It defines `LIBRARY=libcom_err`, objects `error_message.o`, `et_name.o`, `init_et.o`, `com_err.o`, and `com_right.o`, installed headers/share files, shared-library metadata, and targets for `compile_et`, `com_err.pc`, docs, install, uninstall, check, and clean.

## Control Flow
Configure substitution fills build variables. The build compiles static/profile/shared variants through included makefile fragments, creates `compile_et` from `compile_et.sh.in`, generates `com_err.pc`, and `check` regenerates each `.et` test case then diffs generated `.c` and `.h` against checked-in expected files.

## State, Persistence, Dependencies, Risks, and Test Signals
State is generated build output, installed headers/scripts/pkg-config metadata, and test-generated files. Dependencies include top-level make fragments, `config.status`, AWK templates, texinfo tools, and the compiler. Risks include generated-file drift, shared-library ABI flags, and install path substitution errors. Test signals are all `.et` test cases reporting success.
