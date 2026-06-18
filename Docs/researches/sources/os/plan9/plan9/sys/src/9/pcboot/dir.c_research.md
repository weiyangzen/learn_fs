# File Research: sources/os/plan9/plan9/sys/src/9/pcboot/dir.c

## Purpose
Directory/stat utility code for the bootstrap namespace, including stat conversion, union directory reading, and rewriting directory entries for active mount/bind points.

## Main Interfaces
- Exports `dirchstat`, `dirpackage`, `unionread`, `unionrewind`, `mountrockread`, `mountrewind`, and `mountfix`.

## Implementation Notes
- `dirchstat` obtains a channel stat buffer, grows once if needed, and converts with `convM2D`.
- `dirpackage` validates a packed stat buffer sequence and converts it into an array of `Dir`.
- `unionread` walks mounted union elements using `c->uri` and `c->umc`, skipping unreadable components.
- `mountfix` scans directory stat entries and, when an entry is a mount point, stats the mounted channel but preserves the original entry name.
- Overflow entries produced by mount rewriting are saved in `c->dirrock` and returned by later reads through `mountrockread`.

## Dependencies And Risks
- Implements a subset of full Plan 9 directory semantics in the boot environment.
- Error handling intentionally skips failing union components.
- `mountfix` can stash overflow entries but cannot fully solve too-small caller buffers.
