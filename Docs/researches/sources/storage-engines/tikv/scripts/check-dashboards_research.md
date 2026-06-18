# sources/storage-engines/tikv/scripts/check-dashboards

## Purpose
Checks generated Grafana dashboard artifacts against recorded SHA-256 checksums to prevent manual JSON drift.

## Important Commands and Control Flow
With `set -euo pipefail`, the script loops over `./metrics/grafana/*.sha256` and runs `sha256sum -c`. On the first failure it derives the dashboard name, prints guidance to avoid manual modification and run `./scripts/gen-tikv-details-dashboard`, then exits 1. If all checks pass it prints `Dashboards check passed.`

## State, Dependencies, Integration
The script is read-only. It depends on `sha256sum`, dashboard JSON files, and checksum files. It is paired with `scripts/gen-tikv-details-dashboard`, which regenerates both JSON and `.sha256`.

## Risks and Test Signals
It validates bytes, not dashboard semantics. Dashboards without checksum files are not covered. Passing `sha256sum -c` for every checksum is the key signal; intentional JSON edits should fail until the generator is rerun.
