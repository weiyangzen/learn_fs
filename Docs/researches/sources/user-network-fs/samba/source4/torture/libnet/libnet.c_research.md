# sources/user-network-fs/samba/source4/torture/libnet/libnet.c

## Purpose

`libnet.c` registers the smbtorture suite for Samba's libnet convenience interface tests.

## Important APIs, Types, and Functions

- `torture_net_init()` creates the `net` suite, adds simple tests, sets a description, registers the suite, and returns `NT_STATUS_OK`.
- Registered tests cover user management, domain open/close, group management, lookup APIs, RPC connection APIs, share APIs, LSA/SAMR domain operations, BecomeDC, and domain listing.

## Control Flow

Suite initialization is linear: create `net`, add each test by name and function pointer, assign the description, call `torture_register_suite()`, and return success.

## State and Persistence Behavior

The file itself has no persistent state. It exposes tests that may create users, groups, shares, joins, or replicated databases depending on the selected case.

## Dependencies and Integration Points

It depends on smbtorture suite APIs, DCERPC/libnet headers, generated LSA types, and generated prototypes for all libnet torture entry points. It is the integration point that makes the files in this folder runnable.

## Risks and Edge Cases

Registration names are public test selectors, so renames can break automation. The file must remain synchronized with available functions and build inclusion. It mixes destructive and read-only tests under one suite, so callers must select carefully.

## Test Signals

`smbtorture --list` should show `net.*` entries. Link failures catch missing prototypes/functions, while running individual tests validates each registered API path.
