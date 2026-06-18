# File Research: sources/os/linux/linux/block/partitions/atari.c

Implements Atari AHDI and ICD/Supra partition table parsing.

Key responsibilities:
- Rejects devices whose logical block size is not 512 bytes.
- Reads the root sector and validates at least one primary partition entry.
- Emits primary AHDI partitions.
- Follows `XGM` extended partition chains.
- Optionally parses ICD/Supra extra partitions from the root sector.

Important logic:
- `VALID_PARTITION()` checks active flag, alphanumeric ID, and bounds within disk size.
- `OK_id()` accepts `GEM`, `BGM`, `LNX`, `SWP`, and `RAW` IDs for ICD partitions.
- Extended `XGM` parsing reads linked root sectors and emits subpartitions relative to the extended base.

Safety/limitations:
- No strong magic exists for Atari root sectors, so validation is heuristic.
- Extended partition parsing stops on invalid flags, wrong IDs, read failures, or partition limit.
- ICD parsing is attempted only when no AHDI extended partition was seen.

Research relevance:
- This parser illustrates heuristic legacy partition detection and linked extended-partition traversal.
