<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/scripting/bin/samba-tool -->
# sources/user-network-fs/samba/source4/scripting/bin/samba-tool

## Purpose

`samba-tool` is the command-line entry point for Samba's Python netcmd command suite.

## Important APIs, Types, and Functions

It imports `samba.netcmd.main.samba_tool`, installs a default SIGINT handler, and calls `samba_tool(*sys.argv[1:])`.

## Control Flow

The script prepends `bin/python` for source-tree execution, resets SIGINT to default so Ctrl-C terminates immediately, invokes the command dispatcher with all user arguments, and exits with the returned status.

## State and Persistence Behavior

The wrapper itself stores no state. Invoked subcommands may perform extensive AD, filesystem, DNS, or configuration mutations.

## Dependencies and Integration Points

It depends on Samba Python modules and the `netcmd` dispatcher. It is the stable CLI front door for many administrative commands.

## Risks and Edge Cases

Because it delegates all behavior, wrapper risk is mostly environment/path and signal handling. The source-tree `bin/python` insertion can affect module resolution.

## Test Signals

Tests should cover help output, Ctrl-C behavior, return-code propagation, source-tree module resolution, and representative subcommand dispatch.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/scripting/bin/samba-tool -->
