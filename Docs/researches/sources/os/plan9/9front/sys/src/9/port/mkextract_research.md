# File Research: sources/os/plan9/9front/sys/src/9/port/mkextract

General section-field extractor for Plan 9 kernel config files.

Key responsibilities:
- Accepts `[-u] field n file...`.
- Finds indented lines under the named top-level section.
- Prints the nth field from each collected line.
- With `-u`, sorts output uniquely.

Important behavior:
- Ignores blank and comment lines.
- Ends a collection when a non-indented top-level line appears.

Role:
- Reusable build helper for deriving mkfile lists from config sections.
