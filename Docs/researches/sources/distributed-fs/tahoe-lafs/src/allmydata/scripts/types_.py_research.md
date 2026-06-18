# sources/distributed-fs/tahoe-lafs/src/allmydata/scripts/types_.py

## Purpose
Provides shared typing aliases for Tahoe script option declarations and subcommand tables.

## Important APIs, Types, and Functions
Exports `SubCommand`, `SubCommands`, `Parameters`, and `Flags`. `SubCommand` is a tuple of command name, `None`, Twisted `Options` subclass, and description.

## Control Flow
No runtime control flow beyond type alias evaluation at import time.

## State and Persistence Behavior
No state or persistence.

## Dependencies and Integration Points
Depends on `typing` and `twisted.python.usage.Options`. Used by script modules such as `tahoe_invite.py` to annotate subcommand registries.

## Risks and Edge Cases
The comments note that command lists historically used mutable lists, while mypy requires tuple element shapes. Runtime code does not enforce these aliases.

## Test Signals
Coverage is indirect through script imports and CLI command registration tests in `test_cli.py`.
