## sources/test-tools/syzkaller/prog/parse_test.go

Purpose: verifies log parsing behavior for single programs, modern logs with IDs, legacy logs without IDs, unrelated kernel text between program lines, and old fault-injection annotations.

Important APIs/types/functions: `TestParseSingle`, `TestParseMulti`, `TestParseMultiLegacy`, `validateProgs`, `TestParseFault`, and embedded `execLogNew`/`execLogOld` fixtures.

Control flow: tests get the linux/amd64 target, parse static log text with `NonStrict`, validate entry counts, offsets, proc numbers, IDs, program call names, and absence of new fault-injection features except for converted legacy metadata.

State and persistence: no persistence. Test data is in string constants and parsed into in-memory `LogEntry` and `Prog` objects.

Dependencies/integration: depends on generated linux target registration and serializer string forms such as `getpid-gettid`.

Risks: expected program strings couple tests to syscall names and serialization output. The fault test documents a compatibility adjustment from zero-based legacy fault nth to one-based `FailNth`.

Test signals: strong regression signal for parser compatibility across log formats and for offset accounting needed by crash report extraction.
