# sources/sync-backup/syncthing/lib/config/testdata/untrustedintroducer.xml

## sources/sync-backup/syncthing/lib/config/testdata/untrustedintroducer.xml

Purpose: Security regression fixture for untrusted device preparation.

Important data: Version 37 config has an untrusted device marked as introducer and auto-accepting, with one folder shared without an encryption password and another shared with a password.

Control flow and state: `DeviceConfiguration.prepare` clears introducer and auto-accept flags for untrusted devices. `ensureNoUntrustedTrustingSharing` removes trusted shares to untrusted devices unless an encryption password is set or the folder is receive-encrypted.

Dependencies and integration: Used by `TestUntrustedIntroducer`.

Risks and test signals: Protects against accidentally trusting untrusted devices or allowing unencrypted folder sharing with them.
