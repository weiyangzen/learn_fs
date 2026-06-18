# sources/sync-backup/kopia/notification/sender/notification_message_test.go

Purpose: tests the common message parser, serializer, and format validator.

Important APIs/types/functions: `TestParseMessage`, `TestParseMessageNoBody`, `TestToString`, and `TestValidateMessageFormatAndSetDefault`.

Control flow: parse tests feed a subject, valid headers, one invalid header line, a blank separator, and body text; they assert subject/body/header extraction and then round-trip through `ToString` and `ParseMessage`. The no-body test confirms a header-only template is rejected. `TestToString` asserts sorted header order in the rendered form. The format test checks default assignment, `txt`, `html`, and an invalid value.

State and persistence behavior: only in-memory strings/readers are used. Deterministic header ordering is the key persistence-like signal because templates can round-trip consistently.

Dependencies/integration points: validates behavior relied on by all notification senders and template pipelines. Risks/test gaps include duplicated test case name/content, no scanner error simulation, no severity JSON behavior, and no tests for headers containing additional colons beyond the first split. The tests strongly pin accepted formats and the no-body invariant.
