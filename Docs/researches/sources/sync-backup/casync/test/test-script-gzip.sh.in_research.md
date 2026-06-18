# sources/sync-backup/casync/test/test-script-gzip.sh.in

Purpose: compression variant wrapper for the main integration script.

Important APIs/types/functions: `exec @top_builddir@/test-script.sh default gzip`.

Control flow/state: replaces itself with the configured main script using default digest and gzip compression.

Dependencies/integration: relies on Meson substitution and `test-script.sh.in` availability. The main script skips gzip when libz is disabled.

Risks/test signals: useful for catching gzip-specific archive/store regressions while avoiding duplicate test logic.

Source research group: `subset-b-009122`.
