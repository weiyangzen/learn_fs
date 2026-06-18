# sources/sync-backup/casync/test/test-script-xz.sh.in

Purpose: compression variant wrapper for xz.

Important APIs/types/functions: `exec @top_builddir@/test-script.sh default xz`.

Control flow/state: delegates completely to the main integration script, preserving exit status.

Dependencies/integration: requires liblzma-enabled build; the delegated script exits 77 when xz support is unavailable.

Risks/test signals: catches xz compressor/decompressor integration regressions without duplicating the large script.

Source research group: `subset-b-009122`.
