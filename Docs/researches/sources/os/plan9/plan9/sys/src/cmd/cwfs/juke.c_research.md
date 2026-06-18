# File Research: sources/os/plan9/plan9/sys/src/cmd/cwfs/juke.c

HP optical-disc jukebox and WORM side driver. It manages robotic media movement, side discovery, labelled WORM validation, read/write I/O through sd data files, and console jukebox operations.

Key data:
- `Side` tracks one disc side: element number, loaded drive, status, rotation/backside, ordinal label, timing, native block geometry, and Plan 9 block capacity.
- `Juke` tracks robotics, sides, drives, SCSI geometry, fixed-size mode, offline drives, robot handle, and global jukebox list.

Key responsibilities:
- `querychanger()` opens robotics via `openscsi`, registers SCSI target, reads changer geometry, builds side table, reads positions, and initializes drive table.
- `jukeinit()` attaches changer and drive devices, installs console commands, and assigns `Juke*` private pointers to side devices.
- `geometry()` reads SCSI mode pages for element address assignment and transport geometry.
- `positions()`/`element()` read element status and move any discs found in drives back to shelves.
- `wormunit()` ensures a requested side is loaded, spinning/ready, and has known geometry.
- `wormlabel()` validates or writes labelled-WORM label blocks and checks ordinal matches.
- `wormsize()` returns side capacity, hiding the label block for `Devlworm`.
- `wormsizeside()` and `wormsidestarts()` compute side sizes/start offsets in composite device trees.
- `wormread()` and `wormwrite()` perform block I/O to the loaded drive fd.
- `bestdrive()` selects a drive, preferring empty drives or the other side of the same platter, otherwise unloading an old side.
- `wormprobe()` periodically unloads inactive sides.
- Console commands include `wormreset`, `wormeject`, `wormingest`, `wormoffline`, and `wormonline`.

Important interactions:
- Uses SCSI helpers from `scsi.c` for robotics commands (`move medium`, `mode sense`, `read element status`).
- Uses `sdof()`, `inqsize()`, `dataof()`, and normal file I/O for drive data paths.
- Label format is `Label` from `portdat.h`, using `Labmagic`.

Research notes:
- The code supports double-sided media via `rot` and duplicates side entries offset by `nse`.
- `FIXEDSIZE` lets a deployment assume all discs are same size to avoid expensive probing.
- `wormlabel()` may offer to write a new label if the label block is unreadable or magic is bad.
- `wormwrite()` has a typo in an error string (`wormwrwite`) but behavior is unaffected.
