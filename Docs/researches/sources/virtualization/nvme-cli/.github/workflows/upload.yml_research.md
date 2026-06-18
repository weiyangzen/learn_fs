# File Research: sources/virtualization/nvme-cli/.github/workflows/upload.yml

- Purpose: builds and distributes static nvme-cli binaries.
- Triggers: pushes to `master`, `v*` tags, and published releases.
- Build job: computes `git describe` version, runs `scripts/build.sh static`, and packages `nvme-cli-latest-x86_64` plus versioned tag binary when applicable.
- Upload jobs: sends test binaries to an SFTP server and attaches release assets to GitHub releases.
- Secrets: SFTP upload uses username, server, host key, and private key secrets.
