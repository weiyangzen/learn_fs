# sources/user-network-fs/rclone/backend/sftp/sftp_internal_test.go

Purpose: unit tests private helpers in the non-Plan 9 SFTP backend, focusing on shell safety, path encoding, and parser correctness.

Important APIs/types/functions: tests cover `quoteOrEscapeShellPath` for Unix, cmd, and PowerShell; `Fs.remotePath`; `Fs.remoteShellPath`; `parseHash`; and `parseUsage`.

Control flow: shell escaping cases verify harmless paths, command-substitution-like strings, newlines, quotes, Windows cmd quote rejection, and PowerShell single-quote doubling. Path tests instantiate minimal `Fs` values with `encoder.Display | encoder.EncodeColon`, asserting encoded colon handling and `PathOverride` behavior, including `@` root-prefix mode. Parser tests check standard hash command output and multiple `df` layouts.

State and persistence behavior: no persistent state. The tests instantiate only enough `Fs` state to validate deterministic helper output.

Dependencies/integration: uses `testify/assert` and rclone `encoder`. Build tag `!plan9` matches the backend implementation.

Risks/test signals: strong targeted signal for command injection boundaries and shell path construction, which are security-sensitive. It does not test SSH auth, connection pooling, actual command execution, or upload/read behavior.
