# sources/security-integrity/selinux/checkpolicy/test/dismod.c

## Purpose

`dismod.c` is an interactive and scriptable diagnostic utility for displaying the contents of a binary SELinux base policy or loadable module in a textual, module-oriented form. It can show unconditional and conditional AV rules, users, booleans, roles, types/attributes/aliases, role transitions/allows, initial SIDs, requirements, declarations, policy capabilities, unknown handling, filename transitions, version info, and can link an additional module into a loaded base policy.

## Important APIs, Types, and Functions

The file owns a static `policydb_t policydb` and a command table mapping single-character commands to descriptions and flags. `usage()` prints command help, including noninteractive `--actions` mode.

Rendering helpers include `render_access_mask()`, `render_access_bitmap()`, `display_id()`, `display_type_set()`, `display_mod_role_set()`, `display_avrule()`, `display_class_set()`, `display_role_trans()`, `display_role_allow()`, `display_filename_trans()`, and `display_scope_index()`. These convert libsepol values and bitmaps back into readable identifiers and policy-like rule syntax.

Policy loading is handled by `read_policy()`, which peeks at the first 32-bit little-endian word. If it matches `SEPOL_MODULE_PACKAGE_MAGIC`, it reads a module package through `sepol_module_package_read()` after wiring the package policy pointer to the caller's `policydb_t`; otherwise it calls `policydb_read()`.

`link_module()` prompts for a module filename, reads it into a temporary `policydb_t`, indexes it, and calls `link_modules()` against the base. The main loop dispatches commands either from `--actions ACTIONS` or stdin.

## Control Flow

`main()` parses options, initializes and reads the policy, verifies policy type, indexes classes and other symbols, optionally prints version/menu, then repeatedly reads a command. Noninteractive mode consumes one character per loop from the actions string and exits when it reaches implicit `q`. Most commands call display helpers over the loaded `policydb`. The `f` command switches output to a user-selected file; `l` performs module linking; `q` destroys the policydb and exits.

## State and Persistence Behavior

The loaded policydb persists globally until quit. Output state is the current `FILE *out_fp`, initially stdout and optionally changed by command `f`. `link_module()` mutates the loaded base policy by linking in an additional module. The utility does not save the modified policy; it only changes the in-memory model for subsequent display commands.

## Dependencies and Integration Points

It depends on libsepol policydb, services, conditional, link, module, util, and polcaps APIs. It uses endian conversion to detect module package magic. It is built by the local test Makefile and is useful for inspecting outputs produced by checkpolicy/checkmodule.

## Risks and Edge Cases

This is a diagnostic tool, not hardened input-processing code. Many failures call `exit(1)`. Interactive filename handling strips the final byte as a newline and assumes `fgets()` returned a line with length. Some formatting assumes indexed value-to-name arrays are populated. `display_id()` asserts the scope datum exists. Changing output files does not close prior non-stdout handles. Module linking requires the initially loaded policy to be base policy and warns that restart may be needed after failure.

## Test Signals

Build tests should compile with `-Werror`. Runtime tests should load both base and module binaries, exercise `--actions` for every command, verify package and raw policy reading, inspect requirements/declarations for modules, switch output files, test invalid options, and link a valid/invalid module into a base policy.
