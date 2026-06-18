# File Research: sources/os/plan9/9front/sys/src/cmd/spred/fns.h

`spred/fns.h` declares the cross-file function interface for the `spred` sprite editor.

Covered modules:
- File/common helpers: `change`, `filinit`, `filredraw`, `filtitle`, `filtitlelen`, `putfil`, `winwrite`, identity helpers, and `tline`.
- Command helpers: `cmdprint`, `docmd`.
- Window helpers: `emalloc`, `initwin`, `newwin`, `newwinsel`, `resize`, `setfocus`, mouse/window actions, and selection helpers.
- Palette helpers: `newpal`, `findpal`, `readpal`, `writepal`, `putpal`, `paldraw`, `palset`, `palsize`.
- Sprite helpers: `newspr`, `readspr`, `writespr`, `putspr`, `sprsize`.
- Application quit helper: `quit`.

Important interactions:
- This header is the glue between the listed files and adjacent `win.c`.
