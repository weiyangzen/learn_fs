# sources/user-network-fs/samba/source3/utils/net_registry_check.h

## Purpose
This header defines the public option contract and entrypoint for the registry database checker used by `net registry check`.

## Important APIs, Types, And Control Flow
It forward-declares `struct net_context`, defines `struct check_options`, and declares `int net_registry_check_db(const char *db, const struct check_options *opts)`. Options cover dry-run, verbosity, locking, automatic actions, force, repair, assumed registry format version, output database path, wipe/rewrite mode, and whether the database path was implicit.

## State And Persistence
The header has no state. Its fields directly control whether the checker writes the input database, writes a separate output database, wipes output first, cancels changes in test mode, or treats absent version data as the current default for implicit local registry databases.

## Dependencies And Integration Points
It includes `<stdbool.h>`, is implemented by `net_registry_check.c`, and is consumed by `net_registry.c`. It intentionally does not expose reconstructed tree internals or serialized registry record helpers.

## Risks And Test Signals
Like the idmap checker header, it uses the generic name `struct check_options`; including both checker headers in one C file would create a conflicting tag definition. Test signals are compile coverage and option mapping from `net_registry_check()` CLI flags into this structure.
