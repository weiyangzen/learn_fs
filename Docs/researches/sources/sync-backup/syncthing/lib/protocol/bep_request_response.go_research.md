## sources/sync-backup/syncthing/lib/protocol/bep_request_response.go

Purpose: typed request/response structures and wire conversion for BEP block requests.

Important types/functions: `ErrorCode` alias and no-error/generic/no-such-file/invalid constants; `Request` with ID, folder, name, offset, size, hash, weak hash, from temporary flag, and block number; `Response` with ID, code, and data. `toWire` and from-wire functions convert to generated `bep` messages.

Control flow and state: direct field mapping, with integer width conversions for sizes/block numbers.

Dependencies and integration points: used by protocol connections and model request handling; encryption wrappers transform request name/offset/size/hash around these structs.

Risks: size and block number conversions can overflow if callers exceed BEP bounds. Error code mapping is separate in `errors.go`.

Test signals: request integration tests and protocol benchmarks exercise this path indirectly.
