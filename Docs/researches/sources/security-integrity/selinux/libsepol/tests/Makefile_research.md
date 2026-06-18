# sources/security-integrity/selinux/libsepol/tests/Makefile

## Purpose
The test Makefile builds and runs the libsepol CUnit test binary and generates standard/MLS policy fixtures from source policy fragments.

## Important Targets and Integration
`EXE` defaults to `libsepol-tests`. `LIBSEPOL` points to `../src/libsepol.a` for static linkage against internal functions. Parser objects are pulled from `../../checkpolicy/`. `all` builds the binary and generated policies, `policies` builds fixtures, `clean` removes generated artifacts, and `test` prepares downgrade output, builds a reference policy with `checkpolicy`, and runs the suite.

## Risks and Test Signals
Tests depend on CUnit, generated parser objects, m4, and checkpolicy. `mkdir` runs through `env -i` to avoid ASan preload ordering issues. Successful `make test` validates fixture generation, static linkage, and all registered suites in non-MLS and MLS modes.
