# sources/user-network-fs/nfs-utils/tests/nfsconf/01-errors.conf

Purpose: `01-errors.conf` is a negative fixture for the nfs.conf parser.

Important content and control flow: It contains malformed sections, unterminated quotes, missing keys/values, invalid bracket syntax, duplicate-looking assignments, and environment-variable-like data. The file is intended to drive parser diagnostics rather than daemon behavior.

State, dependencies, and integration: There is no runtime state; it is consumed by nfsconf tests or manual parser checks alongside valid fixtures.

Risks and test signals: The fixture is only valuable if the test harness asserts specific failures and recovery behavior. Tests should verify the parser rejects bad section syntax, handles partial assignments predictably, and continues or aborts according to documented error policy.
