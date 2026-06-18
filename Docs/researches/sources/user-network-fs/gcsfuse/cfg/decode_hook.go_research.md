## sources/user-network-fs/gcsfuse/cfg/decode_hook.go

Purpose: Defines the Viper/mapstructure decode hook stack for constructing `Config` structs from flags and config data.

Important APIs/types/functions: `DecodeHook() mapstructure.DecodeHookFunc` composes `TextUnmarshallerHookFunc`, `StringToTimeDurationHookFunc`, and `StringToSliceHookFunc(",")`.

Control flow: when Viper unmarshals, text-unmarshalable custom types are parsed first, then duration strings and comma-separated strings are converted.

State and persistence: stateless factory function.

Dependencies and integration points: uses `github.com/go-viper/mapstructure/v2`; integrates with custom types such as `Octal`, `Protocol`, `DirectPathStrategy`, `LogSeverity`, and `ResolvedPath`.

Risks: hook ordering affects parsing; changing it can break custom type behavior. Comma splitting may surprise callers expecting literal commas.

Test signals: `decode_hook_test.go` covers successful parsing and invalid custom type errors.
