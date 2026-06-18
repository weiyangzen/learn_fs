# sources/security-integrity/selinux/libsemanage/tests/test_fcontext.h

## Purpose
Declares the file-context CUnit suite interface.

## APIs and integration
Exports init, cleanup, and add-tests functions consumed by `libsemanage-tests.c`.

## Risks
No runtime state. Function names must remain synchronized with the runner macro invocation `DECLARE_SUITE(fcontext)`.
