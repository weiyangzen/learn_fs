# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/lib/eps2eps

Shell wrapper for “distilling” Encapsulated PostScript to EPS through Ghostscript.

Behavior:

- Defaults large device dimensions with `-dDEVICEWIDTH=250000 -dDEVICEHEIGHT=250000`.
- Appends leading command-line switches to `OPTIONS`.
- Requires exactly `input.eps output.eps`.
- Executes `gs -q -sDEVICE=epswrite -sOutputFile=... -dNOPAUSE -dBATCH -dSAFER`.

It is a thin CLI adapter around Ghostscript’s EPS writer device.
