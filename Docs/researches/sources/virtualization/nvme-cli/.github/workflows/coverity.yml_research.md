# File Research: sources/virtualization/nvme-cli/.github/workflows/coverity.yml

- Purpose: scheduled/manual Coverity Scan submission.
- Triggers: weekly Monday 00:00 UTC and manual dispatch with optional ref.
- Key behavior: downloads Coverity build tools using secrets, configures Meson, runs `cov-build --dir cov-int ninja -C .build`, archives results, and uploads them to Coverity.
- Guard: runs only in `linux-nvme/nvme-cli`.
- Artifacts: on failure, uploads `cov-int/` and `nvme-cli-coverity.tgz`.
