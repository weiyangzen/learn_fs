# File Research: sources/virtualization/guestfs-tools/align/test-virt-alignment-scan-docs.sh

## Scope

Documentation consistency test for `virt-alignment-scan`.

## Behavior

- Sources common test functions, enables strict shell execution and tracing, then honors skip configuration.
- Runs `podcheck.pl` against `virt-alignment-scan.pod`, passing the common options path.

## Dependencies And Risks

- Requires `podcheck.pl` and the POD file to match the executable option surface.
- Only validates documentation/options, not runtime alignment scanning.
