# File Research: sources/os/plan9/9front/sys/src/cmd/gs/lib/eps2eps

Shell wrapper that distills Encapsulated PostScript to Encapsulated PostScript with Ghostscript.

Behavior:
- Starts with large `-dDEVICEWIDTH`/`-dDEVICEHEIGHT` defaults, then appends leading options.
- Requires exactly `input.eps output.eps`.
- Runs Ghostscript quiet, `epswrite` device, `-dNOPAUSE -dBATCH -dSAFER`, and the collected options.

Filesystem relevance:
- Simple file conversion launcher; no filesystem semantics.
