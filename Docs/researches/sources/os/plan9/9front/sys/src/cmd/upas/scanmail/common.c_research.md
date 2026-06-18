# File Research: sources/os/plan9/9front/sys/src/cmd/upas/scanmail/common.c

Shared scanning/canonicalization and pattern-matching engine for mail/spam scanning.

Key responsibilities:
- Reads message content into memory up to configured limits, identifying header size and ensuring a minimum body sample.
- Canonicalizes headers/body to lowercase, normalized whitespace, stripped HTML tags, decoded quoted-printable-like escapes, and optional base64 body conversion.
- Parses pattern files into regex patterns and hashed string patterns grouped by action.
- Supports pattern actions: dump, hold header, hold, save line, line off.
- Supports alternate exclusion strings with `~~`.
- Matches canonicalized messages against regex/string patterns.
- Prints match context snippets.

Important functions:
- `readmsg()` reads message data and finds end-of-header with fractured-header safeguards.
- `endofhdr()` detects header/body boundary while guarding against lines like `To:`/`Cc:` after a blank.
- `htmlmatch()`, `escape()`, `htmlchk()` strip or preserve relevant HTML tokens.
- `conv64()` decodes base64 then calls `convert()`.
- `convert()` canonicalizes text and detects `Content-Transfer-Encoding: base64`.
- `parsepats()` reads pattern definitions.
- `parsealt()` handles alternate exclusions.
- `extract()` strips comments/quotes and lowercases patterns.
- `matchpat()` matches regex or hashed string patterns and honors alternates.
- `xprint()` emits context around a match.

Filesystem relevance:
- Not a filesystem implementation file, but part of upas mail pipeline operating on message streams and pattern files.

Notable risks and quirks:
- Uses static `ishtml` in `htmlchk()`, so HTML detection state persists across calls unless process flow resets externally.
- `xprint()` backs up with `p--` without explicit lower bound checks before later whitespace search.
- Contains a static base64 decode table tail in this file; related conversion helpers likely depend on declarations from `spam.h`.
