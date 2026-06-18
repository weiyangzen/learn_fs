## sources/sync-backup/syncthing/lib/osutil/replacingwriter.go

Purpose: streaming writer that replaces byte sequences while writing, plus a helper for platform-native line endings.

Important APIs: `ReplacingWriter` has `Writer`, `From`, and `To` fields and implements `Write`. `LineEndingsWriter` returns a writer that maps LF to CRLF on Windows and leaves data unchanged on other platforms.

Control flow and state: `Write` scans input for occurrences of `From`, writes preceding chunks and `To` replacements to the underlying writer, and reports the original input length when all underlying writes succeed. It handles empty/no-match cases by direct write.

Dependencies and integration points: used for text output where newline normalization or simple replacement is needed.

Risks: replacement does not carry partial match state across separate `Write` calls; callers streaming arbitrary chunks can miss patterns split across boundaries. Returned byte count is input length, not bytes written after expansion/contraction, as expected by `io.Writer`.

Test signals: `replacingwriter_test.go` covers several replacement cases.
