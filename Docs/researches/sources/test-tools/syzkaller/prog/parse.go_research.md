## sources/test-tools/syzkaller/prog/parse.go

Purpose: extracts serialized syzkaller programs from executor/manager logs and records offsets, proc IDs, optional program IDs, and legacy fault-injection metadata.

Important APIs/types/functions: `LogEntry`, `Target.ParseLog`, and `extractInt`.

Control flow: `ParseLog` scans line by line. A line containing `executing program ` starts a new entry and finalizes the previous one if a program was parsed. Other lines are appended to a candidate buffer and repeatedly passed to `Deserialize`; the newest successfully parsed program becomes the current entry. Legacy `fault-call` and `fault-nth` markers are translated into `CallProps.FailNth`.

State and persistence: parsing is stateless beyond local offsets, current buffer, current entry, and pending fault metadata. It returns in-memory `LogEntry` objects and does not write data.

Dependencies/integration: uses target-specific `Deserialize` modes. Consumers rely on `Start` and `End` offsets for crash triage and log extraction.

Risks: partial log parsing intentionally ignores deserialization errors until a larger buffer succeeds. The newline handling for data without a trailing newline uses `len(data)-1` and should be considered carefully for empty or malformed inputs. `extractInt` ignores `Atoi` errors after selecting digit-only spans.

Test signals: `parse_test.go` covers single logs, modern and legacy multi-program logs, proc and id extraction, offsets, and legacy fault property conversion.
