# sources/sync-backup/restic/cmd/restic/format.go

Purpose: formats snapshot tree nodes for text `ls` output.

Important APIs/types/functions: `formatNode(path string, n *data.Node, long bool, human bool) string`.

Control flow and state: short mode returns the path only. Long mode maps restic node types to Go file mode bits, formats size as raw decimal or human-readable, appends symlink target when applicable, and returns mode, UID, GID, size, local modtime, path, and target.

Dependencies and integration points: used by `textLsPrinter` in `cmd_ls.go`; depends on `data.Node`, `os.FileMode`, `global.TimeFormat`, and `ui.FormatBytes`.

Risks: local timezone affects output. Device/fifo/socket type mode mapping must match expected CLI conventions. Human-readable width differs from raw width.

Test signals: `format_test.go` covers short, long raw, and long human-readable file output with UTC timezone forced.
