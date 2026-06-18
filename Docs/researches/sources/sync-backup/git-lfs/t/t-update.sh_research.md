<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/t/t-update.sh -->
# sources/sync-backup/git-lfs/t/t-update.sh

Purpose: validates `git lfs update`, which migrates older LFS config keys and hook/config forms to current settings.

Important APIs/functions: uses `git lfs update`, Git config inspection, hook contents, and legacy config such as `lfs.{url}.access`.

Control flow: the main update test constructs legacy filter and hook state and checks update rewrites it correctly. Additional cases cover preserving leading spaces, migrating URL-specific access config, and reporting outside-repo errors.

State and persistence: mutates local/global Git config and hooks in test repositories.

Dependencies and integration points: integrates with installer/update logic, Git config parser/writer, hook templates, and repository discovery.

Risks: updater bugs can destroy user formatting, miss legacy keys, or fail to install required modern filters after upgrades.

Test signals: four cases cover normal update, leading-space preservation, `lfs.{url}.access`, and outside-repo behavior.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/t/t-update.sh -->
