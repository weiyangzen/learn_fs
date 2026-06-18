<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/tools/nfsconf/nfsconfcli.c -->
# sources/user-network-fs/nfs-utils/tools/nfsconf/nfsconfcli.c

## Purpose

`nfsconfcli.c` implements the `nfsconf` command-line editor/query tool for nfs-utils configuration files. It can dump a parsed config, retrieve interpreted or raw entries, check for presence, set a value, or unset a value.

## Important APIs, Types, and Functions

`confmode_t` enumerates mutually intended modes: get, entry, isset, dump, set, and unset. `usage` documents arguments. `main` parses long options with `getopt_long`, configures xlog, calls `conf_init_file`, `conf_report`, `conf_get_section`, `conf_get_entry`, `conf_write`, and `conf_cleanup`. It also writes through the global `modified_by` header string used by the config writer.

## Control Flow

The CLI selects a mode from options, records an optional config path, optional subsection argument, verbosity, dump output file, and modified-header text. Read-only modes initialize the config parser before use. Dump writes the complete report to stdout or a named file. Get, entry, and isset require section and tag and return success only when a value exists. Set and unset require section/tag and optional value, treating an empty string set as unset, then call `conf_write`.

## State and Persistence Behavior

Read modes are transient. Set and unset modify the target config file through `conf_write`, using the support library's preservation and modified-header behavior. The process keeps parsed config state until `conf_cleanup`.

## Dependencies and Integration Points

The file depends on `config.h`, `conffile.h`, and `xlog.h`, and on `NFS_CONFFILE`. It is the user-facing CLI for the same nfs configuration parser used by other nfs-utils components.

## Risks and Edge Cases

Multiple mode options are not rejected; the last parsed mode wins. Set/unset deliberately skip `conf_init_file`, so correctness depends on `conf_write` doing the necessary file read/update itself. Optional-argument handling for `--dump` manually consumes the next positional filename. Argument validation is minimal and returns status 2 for usage errors, 1 for missing values or write failures.

## Test Signals

Tests should cover every mode, custom `--file`, subsection `--arg`, empty-string set-as-unset, `--modified ""`, dump to file failures, last-mode-wins behavior, return codes for missing tags, and verbose logging.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/tools/nfsconf/nfsconfcli.c -->
