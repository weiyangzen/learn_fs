
# sources/user-network-fs/samba/source4/torture/nbt/nbt.c

## Purpose
`nbt.c` is the registration and shared-helper entry point for Samba's NetBIOS over TCP/IP and WINS torture tests. It exposes common NBT socket/name-resolution helpers and registers all NBT-related suites under the top-level `nbt` smbtorture suite.

## Important APIs, Types, And Functions
`torture_init_nbt_socket()` creates an `nbt_name_socket` bound to the torture context's event loop. `torture_nbt_get_name()` constructs a server NBT name from the `host` torture setting, uppercases it, resolves it with `resolve_name_ex()`, and returns the chosen address. `torture_nbt_init()` creates the `nbt` suite, adds register, WINS, datagram, WINS replication, NBT benchmark, and WINS benchmark child suites, sets a description, and calls `torture_register_suite()`.

## Control Flow
NBT tests call the helper functions to obtain sockets and resolved target names. During module initialization, `torture_nbt_init()` builds the suite tree in a fixed order: registration tests, WINS tests, datagram tests, WINS replication tests, NBT query benchmark, and WINS benchmark. The function then publishes the suite to the smbtorture registry.

## State And Persistence
This file stores no persistent state. It allocates sockets and suite objects under caller-provided talloc contexts. The target name/address returned by `torture_nbt_get_name()` is derived from runtime settings and resolver state, not stored globally.

## Dependencies
Dependencies include the NBT client library, torture framework, smbtorture registration API, resolver context, talloc, loadparm, and prototypes for the child NBT suites. A valid `host` setting is required for name resolution.

## Integration Points
This file is the hub that connects `register.c`, `wins.c`, `dgram.c`, `query.c`, `winsbench.c`, and WINS replication tests into the smbtorture suite hierarchy. Its helper functions standardize target resolution for the other files in this subset.

## Risks
If the `host` setting is absent or not resolvable, all dependent NBT tests fail early. Uppercasing the host before resolution is consistent with NetBIOS naming but may hide case-sensitive edge cases unless individual tests override names. Suite registration depends on all referenced child-suite factories being linked.

## Test Signals
Signals are successful suite registration under `nbt`, correct child suite visibility in `smbtorture` listings, and successful name resolution through `torture_nbt_get_name()`. Failures usually appear as assertion messages reporting inability to resolve the configured host.
