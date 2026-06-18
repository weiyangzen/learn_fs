# File Research: sources/local-fs/dlm/dlm_controld/crc.c

## Purpose
Provides `cpgname_to_crc()`, a CRC32 helper used to derive a stable 32-bit id from a CPG/lockspace name.

## Main Behavior
- Contains a static 256-entry CRC32 little-endian lookup table.
- `cpgname_to_crc(data, len)` computes the same result as kernel `crc32_le(0xFFFFFFFF, data, len) ^ 0xFFFFFFFF`.
- Intended to match GFS2/DLM kernel hashing behavior and produce uniform directory/resource hash distribution.

## Integration Points
- Declared in `dlm_daemon.h`.
- Used by `dlm_join_lockspace()` in `cpg.c` to set `ls->global_id` from `dlm:ls:<name>`.

## Risks and Notes
- The function treats input as bytes and does not validate null termination.
- Consistency with kernel CRC behavior is more important than substituting a different hash implementation.
