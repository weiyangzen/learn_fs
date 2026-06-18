# sources/test-tools/stress-ng/core-stressors.h

## Purpose
`core-stressors.h` is the central X-macro registry of stress-ng stressors. It defines the canonical stressor list and macro adapters for enum entries, runtime table elements, and external `stress_*_info` declarations.

## Important APIs, Types, And Functions
`STRESSORS(MACRO)` expands hundreds of stressor identifiers, including this subset's `access`, `acl`, `acct`, `af_alg`, and `affinity`. `STRESSOR_ENUM(name)` emits `STRESS_name` enum values, `STRESSOR_ELEM(name)` emits runtime stressor table rows containing `&stress_name_info`, option IDs, operation IDs, and string names, and `STRESSOR_INFO(name)` emits extern declarations for each `stressor_info_t`.

## Control Flow
The file has no runtime logic. It is included by `stress-ng.c` or related registry code with different macro definitions so the same ordered list generates multiple synchronized structures. Adding, removing, or renaming a stressor changes command-line availability, option dispatch, and info-object linkage.

## State And Persistence
No runtime state is stored here. Its persistent effect is compile-time: the list determines which stressors are represented in the binary and in generated option/help tables.

## Dependencies And Integration Points
It depends on naming conventions across stressor source files: each `MACRO(foo_bar)` must match `stress_foo_bar_info`, `OPT_foo_bar`, and `OPT_foo_bar_ops`. Debian autopkgtests and `kernel-coverage.sh` discover stressors through `stress-ng --stressors`, which is built from this registry.

## Risks
The registry is a high-blast-radius compile-time contract. A missing info object, option constant, or inconsistent underscore spelling causes build failures; incorrect ordering can affect enum/table assumptions. Because shell tests iterate `--stressors`, newly listed stressors are automatically exercised and may need skip rules.

## Test Signals
Successful full build is the primary test. `debian/tests/fast-test-all` enumerates the registry through `--stressors`, while `debian/tests/lite-test` and `kernel-coverage.sh` explicitly exercise many registered names and expose broken table wiring quickly.
