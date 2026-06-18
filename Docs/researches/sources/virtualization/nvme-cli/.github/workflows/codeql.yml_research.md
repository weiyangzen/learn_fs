# File Research: sources/virtualization/nvme-cli/.github/workflows/codeql.yml

- Purpose: CodeQL security/static analysis workflow.
- Triggers: push and pull request on `master`, plus weekly Friday schedule.
- Languages: matrix over `c-cpp` and `python`.
- Key behavior: installs Meson, initializes CodeQL per language, builds with `meson setup --force-fallback-for=json-c .build` and `ninja -C .build`, then runs CodeQL analyze.
- Python config: uses `.github/codeql/codeql-config.yml` to ignore `subprojects`.
