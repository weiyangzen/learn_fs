# sources/sync-backup/kopia/repo/content/content_reader.go

Final split target: `Docs/researches/sources/sync-backup/kopia/repo/content/content_reader.go_research.md`.

Purpose: defines the read-facing content manager interface used by repository layers that need content access without depending on write-manager internals.

Important API: `Reader` exposes compression capability and format access, point reads through `GetContent` and `ContentInfo`, content and pack iteration, active session listing, optional epoch manager access, and full content verification through `VerifyContents`.

Control flow and integration: this file contains only an interface, so behavior is implemented by `WriteManager` and `SharedManager`-backed methods elsewhere in the package. The interface is broad enough for consumers that need maintenance or verification operations, not just plain reads.

State and persistence behavior: no state is stored here. The interface documents which repository operations are expected to be available from a read handle.

Dependencies: `context`, `epoch.Manager`, `format.Provider`, content `ID`, `Info`, iteration option/callback types, session info, and verify options from neighboring content files.

Risks and test signals: because it is an interface, compile-time implementation is the primary signal. Changes are API-sensitive: adding methods forces implementors and tests to update, while removing methods can break repository integration layers.
