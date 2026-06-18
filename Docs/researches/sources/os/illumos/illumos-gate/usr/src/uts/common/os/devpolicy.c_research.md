# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/devpolicy.c

## Purpose

`devpolicy.c` implements illumos device privilege policy lookup and replacement. It keeps a generation-counted table of privilege requirements indexed by major number and minor selector, and returns held `devplcy_t` objects for device vnode access checks.

The policy system is fail-safe at boot: the initial default policy requires all privileges until userland loads a real policy table.

## Main Interfaces

- `devpolicy_init()` initializes locks and creates `nullpolicy`, `dfltpolicy`, and `netpolicy`.
- `dpget()`, `dphold()`, and `dpfree()` allocate and reference-count `devplcy_t`.
- `devpolicy_find()` returns a held policy for a device vnode.
- `devpolicy_load()` validates, parses, and atomically installs a new policy table from userland.
- `devpolicy_get()` copies the current table to userland.
- `devpolicy_getbyname()` resolves a device pathname and returns its effective read/write privilege sets.
- `devpolicy_priv_by_name()` builds an ad hoc policy from privilege-name strings for private minor-node creation.

## Data Model

The global policy table is an array of `tableent_t`, sorted by major number. Each table entry points to a linked list of `devplcyent_t` records. A policy entry can select minors by:

- explicit minor-number range plus block/char type,
- exact minor name,
- simple wildcard minor name with a single `*`,
- all minors via the special `*` expression.

Each policy entry references a `devplcy_t` containing read and write privilege sets and a generation number. `nullpolicy` represents no privilege checks beyond DAC; `dfltpolicy` applies when no specific rule matches; `netpolicy` defaults network drivers to `PRIV_NET_RAWACCESS`.

## Lookup Behavior

`devpolicy_find()` maps clone devices by using the minor as the effective major when `maj == clone_major`. It acquires `policyrw` as reader, binary-searches the major table, and calls `match_policy()` on the matching bucket. If there is no table entry, it asks `devfs_devpolicy()` and then falls back to `netpolicy` or `dfltpolicy`.

`match_policy()` walks the minor list in order. Already-expanded numeric rules compare minor number and vnode type directly. String rules lazily obtain the minor name through `ddi_lyr_get_minor_name()`. Exact string rules may be upgraded in place to numeric minor ranges via `rw_tryupgrade(&policyrw)`, avoiding future string expansion. Wildcard rules are simple single-star prefix/suffix matches.

## Loading And Validation

`devpolicy_load()` requires userland to pass an array of `devplcysys_t` entries with the kernel's exact structure size, at least one entry, and no more than `maxdevpolicy`. Entry zero must be the default policy marker `DEVPOLICY_DFLT_MAJ`.

The remaining entries must be sorted by major number, with explicit rules before wildcard rules, and wildcard rules ordered longest first. The loader rejects duplicate default markers, overlong minor names, and expressions with more than one `*`.

The new table is fully allocated and parsed before it is published. `policymutex` serializes concurrent loads and `policyrw` writer mode performs the atomic swap. `devplcy_gen` is incremented so cached snode policies can detect stale generations.

## Export Behavior

`devpolicy_get()` first copies out the total item count, then fails with `ENOMEM` if the caller's provided item count is too small. Otherwise it serializes `dfltpolicy` and all table entries back into `devplcysys_t` form, preserving wildcard and numeric range forms.

`devpolicy_getbyname()` resolves a user pathname with `lookupname()`, requires a block or character vnode, gets the effective policy via `devpolicy_find()`, and copies only the read/write privilege sets to userland.

## Dependencies

The file depends on kernel privilege set operations, vnode/spec vnode state, devfs policy hooks, layered minor-name lookup, auditing through `audit_devpolicy()`, and DV node policy integration via `devfs_devpolicy()`.

## Notable Invariants And Audit Notes

- `policyrw` protects the active table and default/null policy pointers.
- `policymutex` protects allocation of next-generation policies and serializes table replacement.
- `devpolicy_find()` returns a held policy; callers must release it with `dpfree()`.
- Userland sorting is part of the ABI contract and is revalidated in-kernel before install.
- `match_policy()` can return `dfltpolicy` early if minor-name lookup fails; the nearby comment says `mname` may be set on failure, making this a small leak candidate worth checking against `ddi_lyr_get_minor_name()` semantics.
