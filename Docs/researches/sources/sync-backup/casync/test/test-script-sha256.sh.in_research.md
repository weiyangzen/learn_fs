# sources/sync-backup/casync/test/test-script-sha256.sh.in

Purpose: digest variant wrapper for the main integration script.

Important APIs/types/functions: executes `test-script.sh sha256` to force SHA-256 instead of the default digest.

Control flow/state: no local state; all work is delegated to the main integration script.

Dependencies/integration: targets remoting and archive paths that might accidentally assume SHA-512/256 digest sizes.

Risks/test signals: concise but important compatibility lane for alternate digest algorithms.

Source research group: `subset-b-009122`.
