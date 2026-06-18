# sources/sync-backup/syncthing/internal/slogutil/formatting_test.go

Purpose: Golden-style unit test for the custom slog formatter.

Important APIs/types/functions: `TestFormattingHandler` constructs a `formattingHandler` with `DefaultLineFormat`, a buffer writer, and a fixed UTC timestamp. It logs info, debug, warn, and error records with plain attrs, attrs needing quoting, empty values, nested `slog.Group`s, and logger-level groups.

Control flow: The test emits messages, trims actual and expected output, and fails on exact mismatch while logging both strings. Debug output is expected to be filtered by package-level defaults.

State and persistence behavior: No persistence. It uses an in-memory `bytes.Buffer` and a deterministic `timeOverride`.

Dependencies and integration points: Exercises `formattingHandler`, `Line.WriteTo`, `appendAttr`, `expandAttrs`, `funcNameToPkg`, and global package-level filtering.

Risks: The expected string encodes current group prefix order and package attribution. Any intentional formatter change requires updating the golden output. It does not test syslog priority mode, recorder capture, or source file/line output when package debug is enabled.

Test signals: This is the direct regression signal for human log formatting compatibility.
