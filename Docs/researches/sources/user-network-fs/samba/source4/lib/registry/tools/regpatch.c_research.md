# sources/user-network-fs/samba/source4/lib/registry/tools/regpatch.c

## Purpose

`regpatch.c` implements the `regpatch` command, which applies a registry patch file to a local or remote registry.

## Important APIs, Types, and Functions

`main()` is the only function. It parses `--remote HOST` and `--file PATH`, opens either a remote registry with `reg_common_open_remote()` or local Samba registry with `reg_common_open_local()`, fetches the patch path argument, and calls `reg_diff_apply()`.

## Control Flow

After command-line initialization, popt parsing validates options and obtains credentials/loadparm/event context. Remote mode wins when `--remote` is present; otherwise the command opens local Samba registry. The positional patch filename is required. The command burns argv credentials, applies the diff, frees the talloc context, and exits 0 without checking the `reg_diff_apply()` result.

## State and Persistence Behavior

This tool mutates the target registry according to the patch file. Remote mutations persist on the remote winreg server; local mutations persist in Samba private hives. It does not itself store state beyond transient command context.

## Dependencies and Integration Points

It integrates common registry open helpers, diff loading/application, Samba command-line initialization, credentials, loadparm, and tevent. It is built as `regpatch` with a manpage in `wscript_build`.

## Risks and Edge Cases

The parsed `--file` option is stored but unused; patch input is positional. The return value of `reg_diff_apply()` is ignored, so apply failures can still produce exit status 0. Usage/error paths are minimal, and there is no dry-run mode.

## Test Signals

Tool tests should apply valid dotreg and PReg files to temp local registries, verify failure exit status for malformed or missing patch files, and ensure remote apply errors propagate. Existing `tests/diff.c` covers library apply behavior but not this command's exit handling.

Source-read signal: reviewed complete local file (119 lines).
