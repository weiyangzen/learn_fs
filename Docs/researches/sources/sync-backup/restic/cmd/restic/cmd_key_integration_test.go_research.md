# sources/sync-backup/restic/cmd/restic/cmd_key_integration_test.go

Purpose: end-to-end integration tests for key list/add/passwd/remove behavior and error handling.

Important APIs/types/functions: helpers `testRunKeyListOtherIDs`, `testRunKeyAddNewKey`, `testRunKeyAddNewKeyUserHost`, `testRunKeyPasswd`, `testRunKeyPasswdUserHost`, `testRunKeyRemove`; `emptySaveBackend` corrupts saved key payloads.

Control flow and state: tests initialize repositories, rotate passwords, add keys, remove all non-current keys, reopen with changed passwords, and run `check`. Metadata tests inspect loaded key username/hostname. Failure tests use backend hooks to save empty key files, ensuring passwd/add failures do not break existing access.

Dependencies and integration points: depends on global terminal helpers, repository key loading/searching, backend wrappers, and `testKeyNewPassword`.

Risks: package-global password override requires careful defers. Regex extraction in `testRunKeyListOtherIDs` is coupled to text table formatting. Backend corruption tests cover only one failure shape.

Test signals: strong coverage for key lifecycle, invalid args, empty-password policy, current-key preservation, and repository accessibility after failed key writes.
