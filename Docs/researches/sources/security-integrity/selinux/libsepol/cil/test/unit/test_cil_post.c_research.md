# sources/security-integrity/selinux/libsepol/cil/test/unit/test_cil_post.c

## Purpose
This file tests post-processing comparator functions that order CIL context-related policy records. These comparators are important for deterministic output and conflict/ordering semantics after AST resolution.

## Important APIs, Types, And Functions
It includes `policydb.h`, `CuTest.h`, `CilTest.h`, `test_cil_post.h`, `cil_post.h`, and `cil_internal.h`. Tested APIs are `cil_post_filecon_compare`, `cil_post_portcon_compare`, `cil_post_genfscon_compare`, `cil_post_netifcon_compare`, `cil_post_nodecon_compare`, and `cil_post_fsuse_compare`. The tests initialize `struct cil_filecon`, `cil_portcon`, `cil_genfscon`, `cil_netifcon`, `cil_nodecon`, `cil_ipaddr`, and `cil_fsuse`.

## Control Flow
Each test initializes two objects of the same type, sets only the fields relevant to one comparator branch, calls the comparator with addresses of the object pointers, and asserts sign or equality. Filecon tests cover regex/meta-character and stem/type ordering. Portcon tests cover range width and low port. Genfscon and netifcon compare strings. Nodecon tests cover address family, IPv4 address/mask order, and selected IPv6 byte/mask order. Fsuse tests cover type and filesystem string ordering.

## State And Persistence
All state is temporary heap state initialized by CIL init helpers. No persistence occurs. The ordering result is pure with respect to populated fields, so these tests mostly validate deterministic comparison behavior rather than state mutation.

## Dependencies And Integration Points
The file is registered in `CilTest.c`, although portcon tests are declared in the header but not all appear registered in the suite snippet read. The comparators integrate with CIL post-processing sorting of file contexts, port contexts, genfs contexts, network interface contexts, node contexts, and fsuse records.

## Risks
Tests use minimal object initialization and direct field assignment, so they may miss comparator behavior involving unset strings, full IPv6 arrays, protocol fields, or context tie-breakers. Some assertions check only sign, which is appropriate for qsort comparators but does not ensure magnitude stability. Memory is not freed, relying on process lifetime.

## Test Signals
Strong signals include branch-level ordering coverage for less-than, greater-than, and equality cases across major post-processing comparator families. The file is especially useful for detecting accidental reversal of sort order or changed tie-break priority.
