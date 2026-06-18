# sources/object-store/rustfs/crates/filemeta/src/filemeta/msgp_decode.rs

Purpose: low-level MessagePack decoding helpers used by legacy/custom metadata decoders.

Important APIs/types/functions: `PrependByteReader` replays a previously-read byte before delegating to an inner reader. `read_nil_or_array_len` and `read_nil_or_map_len` accept MessagePack nil or array/map length encodings and return `Option<usize>`. `skip_msgp_value` recursively skips a single MessagePack value, including nested arrays/maps and extension/bin/string payloads.

Control flow: nil-or-length helpers read the marker byte and decode fixed, 16-bit, or 32-bit collection lengths; any other marker returns an error. `skip_msgp_value` reads a marker, computes the number of scalar bytes to discard or recursively skips child elements for arrays/maps, then reads the discard buffer. Extension markers include type bytes plus data bytes.

State and persistence: no persistent state. It consumes bytes from a reader and is used to preserve forward compatibility by skipping unknown fields in persisted MessagePack maps.

Dependencies and integration: uses `rmp::Marker`, `std::io::Read`, and crate `Error`/`Result`. It supports `version.rs` decode paths for old or map-based metadata.

Risks: skipping huge `Str32`/`Bin32`/`Ext32` lengths allocates a vector of that length, so corrupt metadata could cause memory pressure before EOF. `Marker::Reserved` is treated as zero-length skip instead of an error. Ext16/Ext32 skip lengths appear to include more than the one type byte required by MessagePack extension payloads, so changes should be validated against fixtures before reuse.

Test signals: no tests in this module; behavior is indirectly covered by legacy metadata fixture decoding in `filemeta.rs` and `version.rs` tests.
