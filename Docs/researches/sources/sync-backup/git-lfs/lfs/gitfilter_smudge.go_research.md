# sources/sync-backup/git-lfs/lfs/gitfilter_smudge.go

Purpose: implements smudge checkout/download behavior: replace an LFS pointer with local or downloaded content, applying reverse extensions when needed.

Important APIs/types/functions: `SmudgeToFile`, `Smudge`, `downloadFile`, `downloadFileFallBack`, and `readLocalFile`.

Control flow: `SmudgeToFile` removes and recreates the working file preserving mode when possible, then calls `Smudge`; download-declined errors write the pointer placeholder. `Smudge` resolves media path, links/copies from references, validates local object size, downloads if missing and allowed, optionally falls back across remotes, then streams local content. `readLocalFile` applies configured extensions in reverse priority order and verifies extension names/order/OIDs before copying to output.

State/persistence behavior: mutates working-tree files, LFS media files, and config remote selection on successful fallback. Downloads use transfer queues and may create object files.

Dependencies/integration: depends on filesystem helpers, transfer queue manifest, config remotes, `RemoteRef`, pointer extension metadata, progress callbacks, and error wrappers.

Risks/test signals: high user-visible risk: corrupt local objects are deleted on size mismatch, downloads can fail, fallback mutates selected remote, and extension mismatch aborts smudge. Placeholder writing on declined download preserves Git checkout progress.
