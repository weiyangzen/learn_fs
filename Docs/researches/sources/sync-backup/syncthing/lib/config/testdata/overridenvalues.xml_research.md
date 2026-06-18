# sources/sync-backup/syncthing/lib/config/testdata/overridenvalues.xml

## sources/sync-backup/syncthing/lib/config/testdata/overridenvalues.xml

Purpose: Current-version XML fixture covering many non-default option and default values.

Important data: Version 52 config sets custom listen/discovery/local announce, bandwidth, relay/NAT, usage reporting, upgrade, temp/cache, home disk free, release/crash URLs, STUN, notification IDs, feature flags, audit, connection priorities, and folder/device defaults.

Control flow and state: Loading should preserve explicit current-version values, generate `URUniqueID` when usage reporting is accepted and missing, and apply default-folder path from the `<defaults>` section.

Dependencies and integration: Used by `TestOverriddenValues`.

Risks and test signals: Broad regression fixture for avoiding unintended default overwrites in current configs. It also documents deprecated/ignored XML fields that may still appear.
