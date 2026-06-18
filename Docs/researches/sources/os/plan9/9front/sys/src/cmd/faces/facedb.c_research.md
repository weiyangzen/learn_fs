# File Research: sources/os/plan9/9front/sys/src/cmd/faces/facedb.c

## Purpose
Finds, caches, and decodes 48x48 face images for mail senders.

## Key Elements
Caches text files by mtime/read time, translates domains through `.machinelist`, maps `domain/user` entries through `.dict`, recursively searches `/lib/face` and `$home/lib/face`, and falls back to `unknown`. It caches decoded `Facefile` images with reference counts, reads legacy hex face masks, Plan 9 image files, greyscale masks, and 8-bit images converted to 1-bit masks.

## Dependencies
Uses Plan 9 draw images, regexps, directory traversal, environment variables `facedom` and `home`, and the shared `Face`/`Facefile` structures.

## Behavior/Risks
The lookup cache intentionally tolerates stale reads for up to 30 seconds. Recursive directory search skips `512x*` and orders `48x48x8` down to `48x48x1`. `readfile` can leak a newly read buffer if allocating the cache node fails. Bad `.machinelist` regexps call `killall`.
