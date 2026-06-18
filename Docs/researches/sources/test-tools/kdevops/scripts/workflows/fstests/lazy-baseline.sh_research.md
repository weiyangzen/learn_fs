# sources/test-tools/kdevops/scripts/workflows/fstests/lazy-baseline.sh

## Purpose
Automates lazy baseline expunge maintenance for fstests by finding failures common to at least two sections and removing those common entries from section files.

## Important APIs and control flow
The script validates `extra_vars.yaml`, `last-kernel.txt`, and helper scripts, extracts `LAST_KERNEL` and `FSTYP`, constructs `EXPUNGE_DIR="$EXPUNGE_BASE/$LAST_KERNEL/$FSTYP/unassigned/"`, then runs `find-common-failures.sh -l` followed by `remove-common-failures.sh`.

## State and persistence
Mutates expunge files below `workflows/fstests/expunges/<kernel>/<fstyp>/unassigned/`, especially `all.txt`, and may remove emptied files through the helper.

## Dependencies and integration
Depends on the two helper scripts, fstests result metadata, and shell tools. It is a convenience target for curating unstable/common failures into a lazy baseline.

## Risks and test signals
It assumes the `unassigned` priority path and trusts text parsing of YAML. Test with a copied expunge directory before running against tracked data; verify `all.txt` and per-section files contain expected entries.
