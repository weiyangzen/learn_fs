# sources/sync-backup/kopia/repo/blob/config.go

Purpose: defines JSON round-tripping for blob storage connection configuration.

Important APIs/types/functions: `ConnectionInfo`, `UnmarshalJSON`, and `MarshalJSON`. The JSON shape is `{type, config}`, where type selects a registered storage factory and config is decoded into that factory's default config type.

Control flow: unmarshal decodes raw type/config, looks up `factories[type]`, initializes `Config` via `defaultConfigFunc`, and unmarshals raw config into it. Marshal emits the stored type and config. Unknown storage type and malformed config return wrapped errors.

State and persistence behavior: this is a core persistent repository configuration boundary. It stores provider type and provider-specific options used later by `NewStorage`.

Dependencies/integration points: tightly coupled to `registry.go` and every provider's `init` registration. Risks include failure to decode configs if provider packages are not linked/imported, backward-compatibility constraints on provider option JSON, and `Config` being `any` requiring callers to know expected types. Registry tests cover connection info round-tripping.
