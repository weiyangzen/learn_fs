# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/iscannum.c

Implements the scanner’s numeric parser. It is performance-tuned and uses a deliberately dense control flow because number scanning is hot in PostScript workloads. The parser starts with fast integer accumulation, promotes to `long` on overflow risk, and then to `double` for very large or fractional values.

It handles signs, decimal integers, reals, exponent notation, radix notation with `#`, power-of-two radix fast paths, overflow and limit checks, and PostScript syntax errors. It also has a PDF compatibility mode where Acrobat-style invalid fractional forms containing `-` after `.` can be tolerated by swallowing the invalid fractional suffix.

The single exported function, `scan_number`, returns `0` when the whole span is consumed, `1` when a valid numeric prefix was consumed and `*psp` points after it, or a negative Ghostscript error.
