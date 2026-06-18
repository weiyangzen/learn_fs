# sources/storage-engines/rocksdb/options/options_helper.h

Purpose: declares the shared option helper API and enum-name registries used across RocksDB options parsing, serialization, validation, and conversion.

Important APIs, types, and functions: exposes supported compression/checksum discovery, `ValidateOptions`, DB/CF rebuild helpers, configurable wrapper factories, `StringToMap`, `GetStringFromCompressionType`, and the `OptionsHelper` static registry holder. `OptionsHelper` publishes canonical names for DB and CF option structs and maps for compaction styles, priorities, stop styles, temperatures, checksum types, compression types, prepopulate blob cache modes, and encodings. Header-level aliases provide convenient references to those maps.

Control flow: callers use this header to route option conversion without knowing implementation details. DB and CF modules register themselves as `Configurable` through the declared factories; parser and convenience APIs convert between strings/maps and option objects through the declared helpers.

State and persistence behavior: the header declares global static maps whose contents define persisted textual enum names. Changing a string or removing an alias can break options-file compatibility. `StringToMap`'s contract is important for persistence because nested option values remain reusable in `key=value;` contexts.

Dependencies and integration points: includes advanced/public RocksDB option headers, status, and table APIs; forward declares DB/CF mutable and immutable option structs. It sits between `db_options.cc`, `cf_options.cc`, table option code, parser persistence, and public convenience functions.

Risks: static aliases in a header make the registry easy to use but increase coupling to initialization and naming. The checksum helper assumes a contiguous enum range from `kNoChecksum` to `kXXH3`; future enum layout changes would need review. Declared helpers must stay consistent with implementations in `options_helper.cc`.

Test signals: settable tests and parser verification indirectly validate the maps and helper declarations. Unsupported compression discovery depends on runtime compression support and is harder to cover deterministically across builds.
