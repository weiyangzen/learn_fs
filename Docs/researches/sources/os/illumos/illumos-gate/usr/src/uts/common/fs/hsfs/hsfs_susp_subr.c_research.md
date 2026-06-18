# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/hsfs/hsfs_susp_subr.c

## Role

Implements the core SUSP parser used by HSFS to process System Use Areas and continuation areas, including root-directory probing for SUSP/RRIP support.

## Main Behavior

- `parse_sua()` locates the System Use Area inside an ISO directory record, validates lengths, initializes `sig_args_t`, parses signatures, follows continuation areas, and returns name-change or relocation status.
- Defensively rejects negative SUA lengths and SUA ranges extending past the current directory record/block.
- `parse_signatures()` walks SUSP fields, dispatches to handlers for implemented extensions, advances by `SUF_LEN`, detects malformed lengths, and stops on end-of-SUA, relocation, allocation, or validation failures.
- Unknown signatures are skipped using their SUSP length field, with failsafes for short/invalid records.

## Root Probing

- `hs_check_root_dirent()` reads the root directory `.` entry, checks for an initial `SP` signature, invokes the SUSP handler, then runs `hs_parsedir()` twice so RRIP extension records discovered late can affect the cached root vnode metadata.
- If only SUSP and no real extension is found, it clears extension implementation bits and treats the media as plain ISO.

## Continuation Areas

- `get_cont_area()` validates continuation offset/length, reads continuation sectors, and handles areas that cross into the next sector by copying partial data into a zeroed buffer.
- `free_cont_area()` releases continuation buffers.

## Dependencies And Interactions

- Bridges SUSP handlers in `hsfs_susp.c`, RRIP handlers in `hsfs_rrip.c`, and directory parsing in `hsfs_node.c`.
- Uses HSFS warning machinery for inconsistent SUSP/RRIP data.
