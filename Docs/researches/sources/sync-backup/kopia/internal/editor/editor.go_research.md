# sources/sync-backup/kopia/internal/editor/editor.go

Purpose: encapsulates launching an external editor and repeatedly parsing edited content until accepted or aborted.

Important APIs/types/functions: `EditLoop`, package variable `EditFile`, `readAndStripComments`, `getEditorCommand`, and `parseEditor`.

Control flow: `EditLoop` creates a temp directory/file with initial content, invokes `EditFile`, reads content with optional comment stripping, calls caller parse function, and on parse error prompts whether to reopen. `EditFile` resolves editor command from `VISUAL`, `EDITOR`, Windows notepad, or `vi`, then runs it attached to stdio.

State and persistence behavior: temporary edit file is removed by deferred `os.RemoveAll`. No durable state unless the editor itself has side effects.

Dependencies/integration: used by CLI flows needing user-edited JSON/text. Integrates `os/exec`, stdin/stdout/stderr, and Kopia logging.

Risks/test signals: interactive prompt uses `fmt.Scanf`, making automation difficult. `parseEditor` handles simple quoted paths and space splitting but not shell-like escaping. No test file is listed for this item.
