# sources/sync-backup/syncthing/.github/ISSUE_TEMPLATE/config.yml

Purpose: GitHub issue-template configuration. It disables blank issues and provides contact links for support questions and Android-specific problems.

Important APIs/types/functions: `blank_issues_enabled: false` prevents unstructured issue creation. `contact_links` defines forum support and the separate `syncthing-android` tracker with names, URLs, and descriptions.

Control flow: GitHub uses this file when users open a new issue, forcing selection of templates or contact links instead of blank reports.

State and persistence behavior: no application state; affects repository issue creation UI.

Dependencies/integration: integrates with the Syncthing forum and Android repository to route non-core issues away from the main tracker.

Risks/test signals: disabling blank issues may block valid edge cases not covered by forms. The expected signal is fewer support/Android issues in the core repository and more structured incoming reports.
