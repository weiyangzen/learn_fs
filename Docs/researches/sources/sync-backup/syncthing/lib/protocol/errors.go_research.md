## sources/sync-backup/syncthing/lib/protocol/errors.go

Purpose: maps protocol response error codes to Go errors and back.

Important APIs: package errors such as `ErrGeneric`, `ErrNoSuchFile`, and `ErrInvalid`; `codeToError`; `errorToCode`.

Control flow and state: `codeToError` switches BEP error codes to errors, returning nil for no error and generic for unknown/non-success. `errorToCode` uses `errors.Is` style matching or direct comparisons to map known errors to codes and defaults to generic.

Dependencies and integration points: used by request/response handling to translate model request failures into BEP responses.

Risks: preserving `errors.Is` compatibility matters if callers wrap errors. Unknown codes collapsing to generic can hide detail but preserves compatibility.

Test signals: indirect coverage through request tests and protocol connection behavior.
