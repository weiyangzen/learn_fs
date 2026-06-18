# File Research: sources/virtualization/nvme-cli/Documentation/install-webdoc.sh

- Purpose: shell installer/synchronizer for generated web documentation.
- Key behavior: copies changed `.txt`, `.html`, and `.css` documentation into target directory while ignoring `Last updated` differences via `$DIFF`.
- Cleanup: removes stale generated docs from target except release notes and `index.html`.
- Final step: symlinks `git.html` to target `index.html`.
