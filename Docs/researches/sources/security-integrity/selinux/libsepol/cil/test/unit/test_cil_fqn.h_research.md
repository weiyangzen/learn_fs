# sources/security-integrity/selinux/libsepol/cil/test/unit/test_cil_fqn.h

## Purpose
This header declares the FQN unit tests for CuTest registration.

## Important APIs, Types, And Functions
It includes `CuTest.h` and declares `test_cil_qualify_name(CuTest *)` and `test_cil_qualify_name_cil_flavor(CuTest *tc)`.

## Control Flow
The header has no executable control flow. `CilTest.c` includes it and registers both declarations in the tree suite. The implementation then builds ASTs and runs `cil_fqn_qualify`.

## State And Persistence
No state is stored. It provides compile-time linkage only.

## Dependencies And Integration Points
The declarations integrate `test_cil_fqn.c` with the shared CuTest harness. The implementation depends on CIL AST building and FQN qualification internals.

## Risks
Because only two tests are declared, FQN behavior has a small explicit suite surface. Additions to namespace rules may require new declarations and suite registration to avoid relying on incidental coverage elsewhere.

## Test Signals
The header confirms that both general name qualification and a CIL class-flavor qualification path are intended first-class test cases.
