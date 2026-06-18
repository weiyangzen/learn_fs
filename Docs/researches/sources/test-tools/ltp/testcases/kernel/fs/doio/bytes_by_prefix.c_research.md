# sources/test-tools/ltp/testcases/kernel/fs/doio/bytes_by_prefix.c

Purpose: parses human-readable byte strings with optional suffix multipliers into `int`, `long`, or `long long` byte counts for doio tools.

Important APIs/types/functions: `bytes_by_prefix`, `lbytes_by_prefix`, `llbytes_by_prefix`, constants `B_MULT`, `K_MULT`, `M_MULT`, `G_MULT`, `T_MULT`, `DEV_BSIZE`, and `sscanf`.

Control flow: each function scans a numeric prefix and optional single-character multiplier. A plain number is returned directly if nonnegative. Supported suffixes are `b`, `k`, `K`, `m`, `M`, `g`, and `G`, where uppercase variants multiply by the target word-size type. Invalid scan shape, unknown suffix, or negative converted result returns `-1`.

State/persistence behavior: stateless conversion helpers with no external effects.

Dependencies/integration: included by doio/growfiles/iogen style tools through `bytes_by_prefix.h`. Uses `DEV_BSIZE` when available, otherwise falls back to 512.

Risks/test signals: integer versions can overflow silently into negative and then return `-1`; positive wraparound may not be detected. `T_MULT` is defined but unused. Float/double conversion can lose precision for large values.
