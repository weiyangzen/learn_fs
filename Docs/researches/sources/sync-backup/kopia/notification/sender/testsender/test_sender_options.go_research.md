# sources/sync-backup/kopia/notification/sender/testsender/test_sender_options.go

Purpose: defines options for the in-memory test notification sender.

Important APIs/types/functions: `Options` has `Format` and an `Invalid` flag used to force construction failure. `MergeOptions`, `ApplyDefaultsAndValidate`, and `copyOrMerge` mirror other sender option files.

Control flow: merge updates the destination format according to create/update semantics and validates. Validation defaults format to `html`, checks it with `sender.ValidateMessageFormatAndSetDefault`, and then returns an explicit `invalid options` error when `Invalid` is true.

State and persistence behavior: options are JSON-serializable, but this provider is test-only. The `Invalid` flag exists as a controlled failure hook rather than real persisted behavior.

Dependencies/integration points: consumed by `test_sender.go` registration and any tests that need sender creation failure. Risks include the comment saying email provider options and markdown support, both copy/paste artifacts; merge does not copy `Invalid`, so update/create through `MergeOptions` cannot set that failure flag. Tests in this subset cover default creation behavior but not `Invalid` or merge directly.
