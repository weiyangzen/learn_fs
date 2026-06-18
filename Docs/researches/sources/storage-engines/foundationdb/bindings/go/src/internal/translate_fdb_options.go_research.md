<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/go/src/internal/translate_fdb_options.go -->
# sources/storage-engines/foundationdb/bindings/go/src/internal/translate_fdb_options.go

Purpose: generator translating XML `fdb.options` definitions into Go option setters, mutation methods, and enum constants in `fdb/generated.go`.

Important APIs: XML structs `Option`, `Scope`, `Options`; helpers `sanitize`, `writeOptString`, `writeOptBytes`, `writeOptInt`, `writeOptNone`, `writeOpt`, `translateName`, `writeMutation`, `writeEnum`; CLI `main`.

Control flow: reads XML from stdin or `-in`, unmarshals scopes, opens stdout or `-out`, writes file header and `int64ToBytes`, then handles scopes. `*Option` scopes emit receiver methods on `NetworkOptions`, `DatabaseOptions`, or `TransactionOptions`; `MutationType` emits `Transaction` atomic methods; other scopes emit enum types/constants, with `StreamingMode` shifted by +1 so iterator is zero and `ConflictRangeType` made unexported.

State and persistence: writes generated Go source; generated setters change C client configuration at runtime and mutations affect committed transaction state.

Dependencies and integration: depends on XML schema from FoundationDB vexillographer options. Generated output relies on `setOpt`, transaction `atomicOp`, and Go doc formatting.

Risks: uses deprecated `strings.Title`; output is not atomic; output file is not deferred closed on all paths. Name translation may mishandle initialisms compared with idiomatic Go. Hidden options are omitted, so generated API changes with upstream option visibility.

Test signals: no generator tests here; generated code is partly exercised by transaction option and versionstamp tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/bindings/go/src/internal/translate_fdb_options.go -->
