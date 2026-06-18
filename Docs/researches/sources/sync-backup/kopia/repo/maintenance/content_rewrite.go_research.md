# sources/sync-backup/kopia/repo/maintenance/content_rewrite.go

Purpose: rewrites selected contents into new packs to compact short packs, migrate format versions, or rewrite explicit content IDs.

Important APIs/types/functions: `RewriteContentsOptions`, `RewriteContents`, `getContentToRewrite`, `findContentInfos`, `findContentWithFormatVersion`, `findContentInShortPacks`, and `shortPackThresholdPercent`.

Control flow: `RewriteContents` starts parallel workers, consumes content candidates, skips failed candidate lookups, retains contents younger than `SafetyParameters.RewriteMinAge`, and calls `ContentManager().RewriteContent` unless dry-run. Candidate generation can combine explicit IDs, short-pack scanning, and format-version scanning.

State/persistence behavior: successful rewrites create new content/index data and flush the content manager; old packs become unreferenced for later pack GC. Stats distinguish to-rewrite, rewritten, and retained content counts/sizes.

Dependencies/integration: depends on direct repository writer, content reader/manager, blob pack info, index ranges, content logging, stats counters, and maintenance safety windows.

Risks/test signals: duplicate candidates can overcount or attempt repeated rewrites; deleted-content errors may be ignored only with `KOPIA_IGNORE_MAINTENANCE_REWRITE_ERROR`. Tests verify blob deltas and stats for dry-run, prefix-filtered, and short-pack scenarios.
