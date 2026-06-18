# sources/test-tools/syzkaller/pkg/email/parser.go

Purpose: `parser.go` is the main email ingestion module: it reads RFC822 messages, normalizes headers and addresses, extracts body/patch/commands/bug IDs, detects mailing-list authorship, and exposes list utilities.

Important APIs/types/functions: `Email`, `SingleCommand`, and `Command` are core data types. `Parse` is the top-level parser. Address utilities include `AddAddrContext`, `RemoveAddrContext`, `CanonicalEmail`, `EmailsMatch`, and `Split`. Command parsing uses `extractCommands`, `extractCommand`, `strToCmd`, `extractArgsTokens`, and `extractArgsLine`. MIME and metadata helpers include `parseBody`, `ExtractInReplyTo`, `extractBodyBugIDs`, `MergeEmailLists`, `RemoveFromEmailList`, `SubtractEmailLists`, `decodeSubject`, `extractBaseCommitHint`, and `DirectlyAddressedTo`.

Control flow and state: `Parse` reads headers, identifies own addresses with optional plus-context bug IDs, builds deduplicated Cc lists, parses text and attachments recursively, extracts first patch from attachments or body, collects commands from subject plus body, unescapes Google Groups links, handles mailing-list sender/original-from rewrites, parses dates to UTC, and returns a populated immutable result.

Dependencies and integration: it depends on Go `net/mail`, MIME, quoted-printable/base64, regex, URL decoding, and `ParsePatch` from `patch.go`. Lore, dashboard, and sender code consume its normalized output.

Risks: MIME handling keeps only the first text/plain body and ignores non-text non-multipart content. Bug ID regex construction assumes non-empty own emails or domains. Email command restoration is heuristic. Tests in `parser_test.go` cover many real-world encodings and edge cases.
