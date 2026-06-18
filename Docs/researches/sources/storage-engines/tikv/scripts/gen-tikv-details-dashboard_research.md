# sources/storage-engines/tikv/scripts/gen-tikv-details-dashboard

## Purpose
Regenerates Grafana dashboard JSON and checksum files from Python dashboard definitions under `metrics/grafana` using a reproducible Dockerized environment.

## Important Commands and Control Flow
The script computes `root_dir`, builds a `tikv-dashboard-gen` Docker image from `pyfound/black:23.11.0`, installs `isort==5.13.2` and `grafanalib==v0.7.0`, then runs a container mounting `$root_dir/metrics` at `/metrics`. Inside the container it runs isort and black on dashboard Python files, generates each `*.json` via `generate-dashboard`, and writes a `.json.sha256` checksum.

## State, Dependencies, Integration
It mutates dashboard Python formatting, generated JSON, checksum files, and the local Docker image cache. It depends on Docker, Python package availability, grafanalib's generator CLI, and the `metrics/grafana` layout. `scripts/check-dashboards` validates its outputs.

## Risks and Test Signals
The generator both formats source and regenerates artifacts, so runs can create broad diffs. Docker or package resolution failures stop the workflow. Signals are successful image build, generator completion, updated JSON/checksum files, and a subsequent passing dashboard checksum check.
