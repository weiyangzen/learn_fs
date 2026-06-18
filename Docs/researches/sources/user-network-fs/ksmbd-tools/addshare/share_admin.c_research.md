<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/ksmbd-tools/addshare/share_admin.c -->
# sources/user-network-fs/ksmbd-tools/addshare/share_admin.c

## Purpose

Implements the share database mutation engine behind `ksmbd.addshare`. It can prompt interactively for share parameters, complete users/groups/paths, merge command-line `key=value` options, rewrite `ksmbd.conf`, and handle special global-section deletion semantics.

## Important APIs, Types, and Functions

Important functions include `command_add_share`, `command_update_share`, `command_delete_share`, `process_options`, `__prompt_options_stdin`, `new_conf_ml`, `get_conf_contents`, `new_share_nl`, `new_share_kl`, and `__gptrarray_add_share_kl`. It is driven by the `KSMBD_SHARE_CONF` enum and default strings from management/share.h.

## Control Flow

For add/update, options are either supplied by `-o` or generated from existing/default config and edited in raw terminal mode. The selected options are parsed through `cp_parse_external_smbconf_group`, then the whole parser group table is serialized in deterministic-ish share/key order and written with `set_conf_contents`. Delete removes the group, except deleting `global` rewrites global values to defaults.

## State and Persistence Behavior

Persistent state is the full `ksmbd.conf` contents; original formatting and comments are intentionally not preserved except generated comments/default markers. Interactive state includes raw terminal settings and completion lists that are cleared as input changes.

## Dependencies and Integration Points

Depends on GLib arrays/lists/hash tables, passwd/group enumeration, directory reads for path completion, config parser helpers, user/share managers, global root_dir, and kernel share limits.

## Risks and Edge Cases

The raw terminal prompt must restore termios on all exits. Completion and path lookup can observe local system users/groups/directories. Rewriting the full config is simple but can drop manual formatting. The `__defconf_fmt` table must stay 1:1 with `KSMBD_SHARE_CONF`.

## Test Signals

Tests should cover noninteractive `-o` writes, prompt navigation/editing/completion, global section updates, global delete reset, duplicate share rejection, unavailable destination writes, and parse/reload of the generated config.
<!-- END_FILE_RESEARCH: sources/user-network-fs/ksmbd-tools/addshare/share_admin.c -->
