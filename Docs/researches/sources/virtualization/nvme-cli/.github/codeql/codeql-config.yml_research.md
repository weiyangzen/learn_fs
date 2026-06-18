# File Research: sources/virtualization/nvme-cli/.github/codeql/codeql-config.yml

- Purpose: CodeQL configuration used by the Python CodeQL job.
- Key behavior: names the config and excludes `subprojects/**` from analysis.
- Research note: keeps vendored Meson fallback dependencies out of CodeQL findings.
