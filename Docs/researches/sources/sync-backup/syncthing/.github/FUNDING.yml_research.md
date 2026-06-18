# sources/sync-backup/syncthing/.github/FUNDING.yml

Purpose: GitHub Sponsors funding metadata for the Syncthing repository. It advertises the `syncthing` GitHub sponsor target and a custom donation URL.

Important APIs/types/functions: GitHub-recognized keys are `github` and `custom`; other platform keys remain commented examples.

Control flow: GitHub reads this file to render repository funding links. There is no project build or runtime path.

State and persistence behavior: no local state. The file changes repository UI metadata.

Dependencies/integration: integrates only with GitHub repository presentation and external donation handling at `https://syncthing.net/donations/`.

Risks/test signals: stale funding URLs or wrong sponsor handle degrade contributor funding discoverability. The signal is GitHub rendering the Sponsor/Funding link as intended.
