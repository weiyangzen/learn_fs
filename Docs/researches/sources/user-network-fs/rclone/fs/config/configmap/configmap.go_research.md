# sources/user-network-fs/rclone/fs/config/configmap/configmap.go

Purpose: provides a small abstraction for reading/writing configuration from multiple sources with priorities, plus a simple map implementation that can be stringified or base64-encoded.

Important APIs/types/functions: `Priority` values are `PriorityNormal`, `PriorityConfig`, `PriorityDefault`, and `PriorityMax`. Interfaces are `Getter`, `Setter`, and `Mapper`. `Map` stores setter list and priority-sorted getters. Methods include `New`, `AddGetter`, `AddSetter`, `ClearSetters`, `ClearGetters`, `GetPriority`, `Get`, and `Set`. `Simple map[string]string` implements mapper methods plus `Human`, `String`, `Encode`, and `Decode`.

Control flow: getters are stable-sorted by priority so lower numeric priorities win while preserving insertion order within a priority. `GetPriority` scans until priority exceeds the provided max. `Set` writes to every setter. `Simple.string` sorts keys, optionally omits `=true` in human mode, quotes values containing parser-sensitive characters, and doubles single quotes. `Encode` JSON-marshals the map and base64 raw-encodes it; `Decode` strips all whitespace, base64-decodes, and JSON-unmarshals into the map.

State and persistence behavior: `Map` holds references to external getter/setter stores; `Set` mutates all configured setters. `Simple` is in-memory but its string and encoded forms are used in inline remotes and authorization blobs.

Dependencies and integration points: used throughout config loading, backend config, rc update/create, inline remote parsing, and `rclone authorize`. Depends on JSON, base64, sorting, and Unicode whitespace handling.

Risks: not internally synchronized; callers must avoid concurrent mutation. Decode into a nil `Simple` map works only when JSON allocates the map; empty input leaves the map unchanged. String quoting must stay compatible with fspath parser.

Test signals: internal and external configmap tests cover priority, setters/getters, clearing, string/human output, parser round trips, and encode/decode errors.
