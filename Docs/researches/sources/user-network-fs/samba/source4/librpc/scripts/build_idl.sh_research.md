# sources/user-network-fs/samba/source4/librpc/scripts/build_idl.sh

## Purpose

`build_idl.sh` is a small shell wrapper that runs Samba's PIDL generator for source4 librpc IDL files. It supports full regeneration and incremental regeneration based on whether an `.idl` file is newer than its generated `ndr_*.c` output.

## Important APIs, Types, and Functions

The script accepts `FULLBUILD`, `OUTDIR`, and a list of IDL files. It constructs the `PIDL` command with output directory, header, NDR parser, server/client, Python, DCOM proxy, COM header, and include-directory flags.

## Control Flow

The script ensures the output directory exists, builds a PIDL command string, and if `FULLBUILD` equals `FULL`, invokes PIDL on all given IDL files. Otherwise it loops over IDL files, derives `OUTDIR/ndr_<basename>.c`, and adds files to a regeneration list when the generated file is missing or older than the IDL. If the list is non-empty, PIDL runs only on that list.

## State and Persistence Behavior

It writes generated files through PIDL under `OUTDIR`. It does not maintain a manifest; freshness is inferred from filesystem timestamps and generated C file presence.

## Dependencies and Integration Points

Dependencies are POSIX shell utilities, `basename`, `find -newer`, the environment's `PIDL` command, and IDL include path `../librpc/idl`. It is part of the librpc build/generation workflow consumed by Waf build rules.

## Risks and Test Signals

Risks include unquoted variable expansion for paths with spaces, reliance on generated C timestamp rather than all generated outputs, unclear `IDLDIR` use in the full-build log, and command-string construction via shell words. Tests should run full and incremental builds, missing-output regeneration, older/newer timestamp cases, and paths or file names with unusual shell characters if supported by the build system.
