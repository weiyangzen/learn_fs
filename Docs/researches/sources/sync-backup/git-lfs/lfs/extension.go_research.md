# sources/sync-backup/git-lfs/lfs/extension.go

Purpose: pipes clean or smudge data through configured external Git LFS extensions while tracking SHA-256 transformations.

Important APIs/types/functions: `pipeRequest`, `pipeResponse`, `pipeExtResult`, `extCommand`, and `pipeExtensions`.

Control flow: command strings are split on spaces, `%f` is replaced with the filename, subprocesses are chained, input is copied through a pipe while hashing original data, each extension stdout is hashed, output lands in a temp file, processes are waited, outputs are closed, and per-extension input/output OIDs are recorded.

State/persistence behavior: starts external processes and writes a temp file via `TempFile`. A defer kills any started processes on early return. The response owns the temp file path for later clean/smudge use.

Dependencies/integration: used by `GitFilter.Clean` and `readLocalFile` during smudge. Depends on extension config, subprocess management, SHA-256, and temp-file helpers.

Risks/test signals: command splitting is simple and does not honor shell quoting. `extcmds[0]` assumes at least one extension, which callers satisfy. Error buffering is only wired for non-last extension commands, so last-command stderr may be less informative. Extension OID verification in smudge mitigates transformation drift.
