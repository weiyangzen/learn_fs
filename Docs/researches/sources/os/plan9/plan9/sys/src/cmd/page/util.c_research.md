# File Research: sources/os/plan9/plan9/sys/src/cmd/page/util.c

Utility support for `page`: checked allocation, string duplication, temp-file creation, stdin spooling, stdin-to-pipe bridging, and window label updates.

`opentemp` repeatedly applies `mktemp` to a template, creates an ORCLOSE temp file, writes the final name back into the template, and exits on failure.

`spooltodisk` writes the already-read header plus remaining stdin to `/tmp/pagespool...` and returns a seeked fd. `stdinpipe` forks a shared-memory writer process that streams the initial buffer and remaining stdin into a pipe.

`setlabel` writes to `<windir>/label` if possible and deliberately ignores errors.
