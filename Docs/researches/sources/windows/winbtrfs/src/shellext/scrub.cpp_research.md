# File Research: sources/windows/winbtrfs/src/shellext/scrub.cpp

## Purpose
Implements the WinBtrfs scrub UI and command callbacks. It queries scrub status, starts/pauses/resumes/stops scrub operations through driver FSCTLs, and displays scrub progress plus detailed recovered/unrecoverable error reports.

## Main Components
- `format_duration`: locale-aware wrapper around `GetDurationFormatEx`.
- `BtrfsScrub::UpdateTextBox`: builds the multiline status/error text from `btrfs_query_scrub`, fetching a larger scrub report buffer when errors exist.
- `BtrfsScrub::RefreshScrubDlg`: queries current scrub state with `FSCTL_BTRFS_QUERY_SCRUB`, updates buttons, progress bar, status text, and error text.
- `StartScrub`: issues `FSCTL_BTRFS_START_SCRUB`; if the driver reports not-ready, checks balance status to report the clearer “balance running” error.
- `PauseScrub`: queries status and sends either `FSCTL_BTRFS_RESUME_SCRUB` or `FSCTL_BTRFS_PAUSE_SCRUB`.
- `StopScrub`: sends `FSCTL_BTRFS_STOP_SCRUB`.
- `ScrubDlgProc`: dialog procedure with startup refresh, 1-second timer refresh, and button handling.
- Exported callbacks:
  - `ShowScrubW`: elevated GUI dialog entry point.
  - `StartScrubW`: quiet start entry point.
  - `StopScrubW`: quiet stop entry point.

## Data Flow
1. The target volume path is stored in `BtrfsScrub::fn`.
2. Each refresh opens the path with `FILE_TRAVERSE` and backup/reparse flags.
3. Scrub status is queried from the driver.
4. UI controls are updated based on `BTRFS_SCRUB_STOPPED`, `BTRFS_SCRUB_RUNNING`, or `BTRFS_SCRUB_PAUSED`.
5. Error entries are walked using their `next_entry` offsets and formatted as parity, metadata, or data errors.

## Important Dependencies
- `shellext.h`: errors, formatting helpers, handles.
- `scrub.h`: class declaration.
- `resource.h`: dialog and string IDs.
- `../btrfsioctl.h`: scrub and balance FSCTL structures/codes.
- Win32 UI APIs, Common Controls progress bars, locale/date/time formatting.

## Notable Behaviors and Edge Cases
- `UpdateTextBox` only allocates the larger report buffer when `num_errors > 0`; otherwise it formats the initial query result.
- Scrub error summaries count recovered versus unrecovered errors while walking the returned linked buffer.
- The progress percentage divides by `total_chunks`; the code assumes the driver provides a nonzero total while scrub is active.
- Quiet `StartScrubW` and `StopScrubW` intentionally ignore most errors after privilege or open failures, matching fire-and-forget command behavior.
