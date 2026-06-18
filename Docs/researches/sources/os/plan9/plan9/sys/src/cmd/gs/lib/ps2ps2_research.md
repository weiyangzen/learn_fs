# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/lib/ps2ps2

Shell wrapper for distilling PostScript through Ghostscript’s newer `ps2write` device.

Behavior mirrors `ps2ps` except:

- It uses `-sDEVICE=ps2write`.
- It identifies as revision 1.1 in the source header.

The script requires `input.ps output.ps` and passes optional leading Ghostscript switches.
