# sources/test-tools/syzkaller/pkg/email/lore/parse.go

Purpose: `lore/parse.go` groups parsed lore.kernel.org emails into dashboard discussion threads and patch series.

Important APIs/types/functions: `Thread`, `Series`, and `Patch` are the core outputs. `Threads`, `PatchSeries`, `DiscussionType`, `parsePatchSubject`, `LinkToMessage`, and `LinkToThread` are public or package-significant helpers. `PatchSubject` and generic `Optional[T]` represent parsed subject metadata.

Control flow and state: `listThreads` records messages by `Message-ID`, builds parent-to-child edges from `In-Reply-To`, starts traversal from roots or orphan replies, then applies `email.NewMessageAction` to append, ignore, or create threads. Bug IDs are collected and sorted per thread. `PatchSeries` reuses shallow thread traversal, parses the root patch subject, collects cover/base-commit data, ignores cover seq 0 and non-patch replies, detects duplicates, sorts patches by sequence, and marks corrupted series when counts do not match.

Dependencies and integration: it layers on `pkg/email` parsing and action logic plus dashboard discussion-type constants. Link helpers encode lore.kernel.org URL shape.

Risks: patch subject parsing is regex-based and intentionally crude; unusual subject tags may be missed. Thread traversal depends on complete message IDs and can split orphan replies. Series corruption reasons are strings consumed by callers. Tests in `parse_test.go` cover thread grouping, subject parsing, discussion type, series parsing, and links.
