# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/OzoneTrash.java

## Purpose
`OzoneTrash` is an Ozone-specific wrapper around Hadoop `Trash` that installs `TrashPolicyOzone` so OM can run a trash emptier with Ozone-aware behavior.

## Important APIs, types, and functions
- The constructor calls the Hadoop `Trash` constructor and creates `new TrashPolicyOzone(fs, conf, om)`.
- `getEmptier()` delegates to the Ozone trash policy's emptier.

## Control flow
`OzoneManager.startTrashEmptier()` creates a `TrashOzoneFileSystem`, constructs `OzoneTrash`, obtains the emptier runnable, and runs it in a daemon thread. This class only chooses the policy and returns its runnable.

## State and persistence behavior
The only field is `trashPolicy`. Trash checkpointing and deletion state are handled by `TrashPolicyOzone` and the supplied `FileSystem`; this wrapper does not persist anything directly.

## Dependencies and integration points
It depends on Hadoop `Trash`, `TrashPolicy`, `FileSystem`, `Configuration`, and Ozone `TrashPolicyOzone`. It is integrated into OM lifecycle through `startTrashEmptier()` and `stopTrashEmptier()`.

## Risks and edge cases
If `TrashPolicyOzone` construction fails, OM trash emptier startup fails and can abort OM start for invalid trash interval or filesystem setup errors. Since `getEmptier()` bypasses the superclass policy, any Hadoop `Trash` behavior changes are only inherited for construction-level setup, not emptier selection.

## Test signals
Tests should verify the wrapper returns the `TrashPolicyOzone` emptier, propagates construction and `getEmptier()` IOExceptions, and integrates with OM trash interval handling for disabled, negative, and positive intervals.
