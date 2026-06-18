# sources/security-integrity/selinux/checkpolicy/test/dispol.c

## Purpose

`dispol.c` is an interactive and scriptable diagnostic utility for reading a binary SELinux policy file and rendering selected policydb contents in text form. It is explicitly test-oriented: the header describes it as a binary policy display program that focuses on AVTAB and conditional AVTAB rules, but the current implementation also displays booleans, conditional expressions, policy capabilities, classes, users, roles, types, attributes, permissive types, role transitions, filename transition rules, and unknown-class handling.

## Important APIs, Types, And Functions

The file is tightly coupled to libsepol internals through `policydb_t`, `policy_file`, `avtab_t`, `avtab_key_t`, `avtab_datum_t`, `cond_node_t`, `cond_expr_t`, `role_trans_t`, `filename_trans_key`, `filename_trans_datum`, `ebitmap_node_t`, and symbol tables such as `p_type_val_to_name`, `p_class_val_to_name`, and `sym_val_to_name`.

`commands[]` defines the UI and noninteractive action set. Its `CMD`, `HEADER`, and `NOOPT` metadata drive `usage()` and `menu()` display, while `main()` directly switches on the action character.

Rendering helpers include `render_access_mask()`, `render_type()`, `render_key()`, and `render_av_rule()`. `render_av_rule()` is the central formatter: it filters conditional rules by `RENDER_UNCONDITIONAL`, `RENDER_ENABLED`, `RENDER_DISABLED`, and `RENDER_CONDITIONAL`, then prints allow/auditallow/dontaudit, type transition/member/change, and extended-permission forms using `sepol_av_to_string()` and `sepol_extended_perms_to_string()`.

Display commands are implemented by `display_avtab()`, `display_expr()`, `display_cond_expressions()`, `display_handle_unknown()`, `display_booleans()`, `display_policycaps()`, `display_classes()`, `display_users()`, `display_roles()`, `display_types()`, `display_attributes()`, `display_permissive()`, `display_role_trans()`, and `display_filename_trans()`. `change_bool()` mutates an in-memory boolean and calls `evaluate_conds()` so later conditional displays reflect the new state.

## Control Flow

`main()` accepts `binary_pol_file` or `-a/--actions ACTIONS binary_pol_file`. It opens the policy, stats it, maps it privately with read/write permissions, initializes a memory-backed `policy_file`, initializes `policydb`, and calls `policydb_read()`. In interactive mode it prints progress and the menu; in action mode it consumes one character per action and defaults to `q` when the action string is exhausted.

The command loop dispatches numbered AVTAB and conditional commands, metadata commands such as classes/types/users/roles, output redirection via `f`, filename transition display via `F`, and shutdown via `q`. Interactive boolean changes prompt for a name and state; noninteractive actions cannot supply the boolean name/state because command `7` is marked `NOOPT` only in the menu metadata and still prompts through stdin.

## State And Persistence

The binary policy is loaded into memory and represented in `policydb`. `change_bool()` is the only policy state mutation and is deliberately in-memory only; the original policy file is not rewritten. Output state is held in `out_fp`, which can be switched to a newly opened file by the `f` command. The program destroys `policydb` only on the explicit `q` path, not on all error exits.

## Dependencies And Integration Points

The utility depends on libsepol policydb headers and functions, POSIX file APIs, and `mmap()`. It integrates with checkpolicy/libsepol tests by providing a way to inspect binary policy internals after compilation. Its output uses libsepol string formatting for access vectors and extended permissions, so changes in libsepol canonical output can affect tests or users of this diagnostic.

## Risks And Edge Cases

Several functions index libsepol value-to-name arrays with `value - 1`; malformed or unexpected policydb values could cause invalid reads. `render_key()` checks source and target type names but not `tclass` before printing. `display_id()` assumes the symbol name exists. The mapping requests `PROT_READ | PROT_WRITE` even though the file is opened read-only and mapped `MAP_PRIVATE`, which may be less portable than a read-only mapping. Error paths after `open()`, `fstat()`, `mmap()`, `policydb_init()`, or `policydb_read()` exit without centralized cleanup. `ans[strlen(ans) - 1] = 0` assumes non-empty input lines. Output file handles are overwritten without closing a previous non-stdout file.

## Test Signals

Useful tests compile a small binary policy, run `dispol -a` across actions `1` through `6` and metadata commands, and compare stable substrings for AV rules, booleans, policycaps, classes, roles, types, permissives, and unknown handling. Conditional tests should flip booleans interactively or through a scripted stdin path and verify `evaluate_conds()` changes enabled/disabled rendering. Fuzz or negative tests should cover unreadable files, invalid policy blobs, and policies with sparse symbol names.
