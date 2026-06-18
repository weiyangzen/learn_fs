# sources/user-network-fs/samba/source4/lib/registry/tools/common.c

## Purpose

`tools/common.c` provides shared open helpers for source4 registry command-line tools. It hides the choice between remote winreg, local Samba registry, and a single hive file imported into a local registry context.

## Important APIs, Types, and Functions

`reg_common_open_remote()` calls `reg_open_remote()` and prints failures. `reg_common_open_file()` opens a hive with `reg_open_hive()`, creates a local registry context, and imports the hive root as a registry key. `reg_common_open_local()` calls `reg_open_samba()`.

## Control Flow

Each helper attempts one backend open path, checks `WERROR`, reports to stderr on failure, and returns either a registry context or start key. File opens use the supplied event, loadparm, and credentials objects for backend selection and LDB access. The imported file key's context is used by tools that traverse or edit a standalone hive.

## State and Persistence Behavior

Remote opens mutate remote state only when callers later perform operations. Local opens may create or update Samba private LDB hives through `reg_open_samba()`. File opens can return a mutable imported hive root, and changes persist according to the backing hive backend.

## Dependencies and Integration Points

It depends on credentials, tevent, loadparm, and the registry library. `regpatch`, `regshell`, and `regtree` all use these helpers; `regdiff` has its own open-backend helper for two-context diffing.

## Risks and Edge Cases

The helper prints errors but drops detailed ownership and cleanup information. `reg_common_open_file()` returns a key instead of a context, so callers must treat file mode differently. Importing with predef key `-1` relies on local registry import semantics and may not expose normal predefined-key behavior.

## Test Signals

Tool smoke tests should cover `--remote`, local default, and `--file` modes, including failed connection/file paths. Existing registry tests cover underlying APIs but not these stderr/reporting wrappers directly.

Source-read signal: reviewed complete local file (88 lines).
