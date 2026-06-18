# sources/test-tools/kdevops/scripts/workflows/fstests/copy-results.sh

## Purpose
Copies the latest fstests results tarball and kdevops config into a separate results archive repository.

## Important APIs and control flow
The script validates `kdevops-results-archive` exists next to the current checkout and contains an `fstests` subdirectory. It ensures `workflows/fstests/results/archive` is a symlink to that archive, validates `extra_vars.yaml`, `last-kernel.txt`, and the result tarball, derives filesystem type and provider type, then creates a date/count archive directory.

## State and persistence
Creates symlink `workflows/fstests/results/archive`, copies `${LAST_KERNEL}.xz` and `.config` into `archive/$USER/$FSTYP/$TYPE/YYYYMMDD-NNNN`, then runs `git add` in the archive repository.

## Dependencies and integration
Requires shell tools, Git, `extra_vars.yaml`, and fstests result layout. It supports manual archival after baseline/test runs.

## Risks and test signals
The provider type is inferred from grepping YAML and can misclassify. It stages changes in another repo but does not commit. Test with a scratch archive repo, existing count directories, and missing tarball failure paths.
