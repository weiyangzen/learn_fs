# File Research: sources/os/plan9/plan9/sys/src/cmd/abaco/dat.h

Central Abaco data model and UI/API declaration header.

Key contents:
- Defines `Runestr`, editable `Text`, layout `Line`/`Box`/`Lay`, cached image `Cimage`, URL `Url`, `Page`, `Window`, `Column`, `Row`, command `Exec`, and `Timer`.
- Declares text, box, layout, page, window, column, and row operations.
- Defines UI constants for margins, scrollbars, box sizes, tab spacing, buffer sizes, stack size, and colors.
- Declares global mouse, keyboard, image, font, row, selection, active column, webfs mount, plumbing, charset, and refresh channels.

Dependencies:
- Relies on Plan 9 draw/frame/plumb/html types such as `Frame`, `Image`, `Font`, `Docinfo`, `Item`, `Table`, and `Kidinfo`.

Notable risks:
- Many globals are declared in this header, so compilation units share mutable UI state broadly.
- `Url` uses manual reference counting; page/window history code must balance it.
