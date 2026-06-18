## sources/sync-backup/rsync/testsuite/output-options_test.py

Purpose: breadth coverage for rsync output/reporting options rather than path semantics.

Important APIs and control flow: defines `out(*args, want_rc=0, env=None, text=True)` to capture output and require expected return codes. It checks `--version`, `--help`, `-i`, `--dry-run`, `--stats`, `--out-format=%n`, `--list-only`, `--quiet`, `--progress`, `-h`, and `-8`. For each successful transfer option it also verifies behavior, such as dry-run/list-only not creating files and quiet still transferring.

State and dependencies: rebuilds source/dest trees multiple times, creates a 50 KiB file for human-readable stats, and attempts a high-bit filename under `LC_ALL=C` for `-8`.

Integration points: validates CLI output contracts, itemize/stat formatting, progress output, and filename escaping.

Risks and test signals: output formats can intentionally change, but checks are documented-shape assertions. The high-bit filename case is best effort where filesystems preserve raw bytes.
