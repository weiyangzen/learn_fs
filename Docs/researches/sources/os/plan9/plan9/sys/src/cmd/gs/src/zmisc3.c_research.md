# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/zmisc3.c

Miscellaneous LanguageLevel 3 operators. It registers `clipsave`, `cliprestore`, and `.eqproc`.

`clipsave` saves clipping state through the graphics state, and `cliprestore` restores it. These are thin wrappers around the clipping save/restore support in `gsclipsr.h`.

`.eqproc` compares two procedure objects structurally. It checks procedure-like operands and delegates to the interpreter’s procedure comparison logic, returning a boolean result. The file is a narrow LL3 extension binding.
