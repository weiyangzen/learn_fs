# sources/sync-backup/kopia/notification/sender/email/email_sender_options.go

Purpose: defines configuration and merge/default behavior for the email notification provider.

Important APIs/types/functions: `Options` contains SMTP server, port, identity, username/password, sender/recipient fields, CC, and format. `MergeOptions` overlays source values onto a destination, `ApplyDefaultsAndValidate` fills default port/format and enforces required fields, and `copyOrMerge` implements create-vs-update semantics for comparable fields.

Control flow: `MergeOptions` copies every field when creating a configuration, but during update only non-zero source values replace destination values. It then validates the merged result. Validation defaults port to `587`, requires SMTP server, from address, and to address, then calls `sender.ValidateMessageFormatAndSetDefault` with default `html`.

State and persistence behavior: this file only mutates the passed `Options` value. Password is marked sensitive for Kopia serialization. The struct is the persistent JSON shape used by method configuration and must remain backward compatible.

Dependencies/integration points: used by `email_sender.go`, CLI/profile merge paths, and sender registry JSON unmarshalling. Risks include inability to clear a field during update because zero values are ignored, the misleading comment that format can be `md` while validation accepts `txt`/`html`, and `CC` being merged/validated but not used by the sender. Tests cover required-field failures, defaults, and update merge behavior.
