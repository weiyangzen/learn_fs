# sources/sync-backup/kopia/notification/sender/sender_config.go

Purpose: provides JSON serialization/deserialization for configured notification methods.

Important APIs/types/functions: `Method`, `MethodConfig`, `UnmarshalJSON`, `Options`, and `MarshalJSON`. The JSON shape is `{type, config}` and `config` is decoded according to the registered sender type.

Control flow: `UnmarshalJSON` first decodes raw type and raw config, verifies a sender factory exists in `allSenders`, seeds `Config` from `defaultOptions[type]`, then unmarshals the raw config into that typed value. `Options` re-marshals the stored config into a caller-provided result type. `MarshalJSON` emits the type and config as-is.

State and persistence behavior: this is a persistent profile configuration boundary. Compatibility depends on stable method names and option struct JSON tags. It does not itself validate provider options beyond requiring registration and JSON decodability.

Dependencies/integration points: tightly coupled to `sender.Register` and global default options. Risks include pointer/value subtleties because `defaultOptions` stores a zero value, not a pointer, and unknown sender types fail during unmarshal. Test signals are mostly indirect via provider tests; the file has no dedicated test in this subset.
