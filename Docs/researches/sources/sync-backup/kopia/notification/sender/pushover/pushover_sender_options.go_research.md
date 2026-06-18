# sources/sync-backup/kopia/notification/sender/pushover/pushover_sender_options.go

Purpose: defines Pushover provider configuration and update semantics.

Important APIs/types/functions: `Options` contains app token, user key, body format, and an optional endpoint override. `ApplyDefaultsAndValidate` enforces credentials and defaults the format to plain text. `MergeOptions` overlays app token and user key only; `copyOrMerge` implements create/update behavior.

Control flow: validation fails when `AppToken` or `UserKey` is empty, then delegates format validation to `sender.ValidateMessageFormatAndSetDefault` with default `txt`. Merge copies non-zero values during update and all values during create, then validates the destination.

State and persistence behavior: this is the JSON-persisted sender configuration. Tokens are not marked `kopia:"sensitive"` in this file, which is notable compared with other credential structs.

Dependencies/integration points: consumed by `pushover_sender.go` registration and profile update commands. Risks include `MergeOptions` not merging `Format` or `Endpoint`, so updates cannot change those via this helper, and comments again mention markdown while validation allows only text/html. Tests cover credentials/defaults indirectly, but do not expose the missing `Format`/`Endpoint` merge behavior.
