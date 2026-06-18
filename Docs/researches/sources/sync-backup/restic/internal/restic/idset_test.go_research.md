
# sources/sync-backup/restic/internal/restic/idset_test.go

Purpose: tests map-backed ID set behavior.

The tests create known IDs, insert and delete entries, verify `Has`, `Len`, and `Equals`, inspect sorted `List` and compact `String` output, and exercise set algebra such as `Merge`, `Sub`, `Intersect`, and subset checks. They also confirm empty and nil-ish behavior remains stable.

State is local ID sets. Integration points are prune/repair/lock workflows that rely on precise set membership. Risks covered include duplicate insertion changing length, delete behavior, unstable ordering after list conversion, and incorrect set algebra leading to wrong pack removal or retention decisions.
