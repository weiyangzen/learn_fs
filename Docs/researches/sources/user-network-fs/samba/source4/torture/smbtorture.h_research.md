# sources/user-network-fs/samba/source4/torture/smbtorture.h

## Purpose
`smbtorture.h` is the public header for the smbtorture runner and suite registration layer. It declares global torture runner settings, the root suite pointer, runner lifecycle functions, test dispatch/listing functions, target parsing, and documents target capability flags consumed by tests.

## Important APIs, Types, and Functions
The header declares `torture_root`, `torture_entries`, `torture_seed`, `torture_numops`, `torture_failures`, and `torture_numasync`. Public functions include `torture_init()`, `torture_register_suite()`, `torture_shell()`, `torture_print_testsuites()`, `torture_run_named_tests()`, and `torture_parse_target()`. It forward-declares `struct smbcli_state` and `struct torture_test` and includes the central `../lib/torture/torture.h` harness header.

## Control Flow
The header itself has no runtime control flow, but it defines the interface between module init functions and the smbtorture executable. Modules call `torture_register_suite()` to add suites under `torture_root`; `smbtorture.c` calls `torture_init()` and `torture_run_named_tests()`; tests read settings documented here to adapt expectations to server targets.

## State and Persistence Behavior
All declared globals are process-lifetime runner state. The long comment block describes `torture:*` loadparm settings such as `invalid_lock_range_support`, `sacl_support`, `resume_key_support`, `rewind_support`, `ea_support`, `search_ea_support`, and `hide_on_access_denied`; these settings persist in the loadparm context for the duration of a run.

## Dependencies and Integration Points
This header is included by runner code and suite registration files throughout `source4/torture`. It ties server capability policy to command-line target parsing and lets individual tests avoid hard-coded server names by reading feature flags.

## Risks
The documented feature flags are a compatibility contract. Misspelled or inconsistent setting names cause tests to default to full support and may produce false failures against older or partial servers. Global variables make runner behavior process-wide and unsuitable for independent concurrent runner contexts within one process.

## Test Signals
The header has no direct tests, but successful compilation of torture modules and correct target-specific skips or expected-status changes are indirect signals that this interface remains coherent.
