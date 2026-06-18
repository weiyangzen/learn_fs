# File Research: sources/os/plan9/9front/sys/src/cmd/cwfs/main.c

Purpose: Main entry point for the user-mode cached-WORM file server. It parses options, initializes global configuration, posts 9P and command services, starts network/listener/server workers, and runs background copy/sync loops.

Key globals:
- `devmap`: optional device remapping table loaded from `-m`.
- `bin`: console input `Biobuf` used by confirmation prompts.
- `chatty`: diagnostic verbosity.
- `sfd`: stdio service fd for `-s`.

Important behavior:
- `confinit()` sets default counts for users, server workers, files, message buffers, path table size, and calls platform-specific `localconfinit()`.
- `mapinit()` reads a two-column device map file, validates source configs, and maps config strings either to device configs or replacement files.
- `postservice()` posts the filesystem service to `/srv/<name>` and command service to `/srv/<name>.cmd`; with `-s`, it first serves 9P on inherited stdio.
- `main()` initializes formatting, memory, queues, message buffers, networking, SCSI, file/path/user tables, iobufs, system config, services, console command handling, and worker processes.
- `serve()` is the multi-worker 9P dispatch loop. It receives `Msgbuf`s from `serveq`, locks channel/main state, detects or reuses the protocol handler, and frees messages.
- `rahead()` batches and sorts readahead requests by device/address before issuing `getbuf(..., Brd)`.
- `wormcopy()` schedules automatic daily dumps, copies dirty cache blocks to WORM, and calls `wormprobe()` for jukebox idle handling.
- `synccopy()` writes sync blocks periodically.
- `inqsize()` reads an sd-style `ctl` file and extracts the reported geometry block size.

Notable details:
- `maxsize()` computes maximum addressable file size with overflow detection, based on direct and indirect block fanout.
- `nextdump()` computes the next automatic dump time using `nextime()`.
- `exit()` marks the server as exiting, prints halt time, posts a process-group note, and exits.
