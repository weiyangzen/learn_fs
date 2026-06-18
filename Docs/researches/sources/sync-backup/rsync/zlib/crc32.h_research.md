# sources/sync-backup/rsync/zlib/crc32.h

Purpose: generated static CRC lookup tables for `zlib/crc32.c`.

Important content: declares `local const z_crc_t FAR crc_table[TBLS][256]`. The first table supports byte-at-a-time CRC updates; additional tables under `#ifdef BYFOUR` support little-endian and big-endian word-at-a-time CRC processing. Values are precomputed for the standard CRC-32 polynomial used by zlib.

Control flow and state: no executable control flow. The header is included only when `DYNAMIC_CRC_TABLE` is not defined, making table initialization compile-time data rather than runtime generation.

Dependencies and integration: tightly coupled to `crc32.c` macros `TBLS`, `BYFOUR`, `local`, `FAR`, and `z_crc_t`. Risks are table/source mismatch if regenerated with different polynomial or formatting assumptions, and code size from static tables. Test signals are CRC output compatibility and compressed stream integrity; any corruption here would surface broadly in zlib consumers.
