# sources/sync-backup/restic/cmd/restic/cmd_key_passwd.go

Purpose: implements `restic key passwd`, replacing the currently used key/password with a newly created key and removing the old one.

Important APIs/types/functions: `KeyPasswdOptions` embeds `KeyAddOptions`; `runKeyPasswd`; `changePassword`.

Control flow and state: rejects positional arguments, opens repository under an exclusive lock, obtains the new password through the same path as key add, creates a new key from current key material, records old key ID, validates access through the new key, removes the old key, and prints the new key ID. Persistent state changes include one new key file and deletion of the old key file.

Dependencies and integration points: reuses `getNewPassword` and `switchToNewKeyAndRemoveIfBroken`; uses repository `AddKey` and `RemoveKey`.

Risks: failure after new key creation but before old key removal can leave multiple valid keys. Failure in key validation attempts rollback. Exclusive lock is appropriate because this command removes a key.

Test signals: key integration tests cover password rotation, username/hostname metadata, invalid args, and corrupted save failure with old password still usable.
