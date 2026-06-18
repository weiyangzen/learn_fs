# File Research: sources/virtualization/guestfs-tools/builder/test-docs.sh

## Scope

Documentation consistency test for builder tools.

## Behavior

- Runs `podcheck.pl` on `virt-builder.pod`, inserting common customize synopsis/options POD fragments and ignoring signature options.
- Runs `podcheck.pl` on `virt-builder-repository.pod`.

## Dependencies And Risks

- Depends on common customize POD fragment paths.
- Only checks documentation/option consistency, not runtime builder behavior.
