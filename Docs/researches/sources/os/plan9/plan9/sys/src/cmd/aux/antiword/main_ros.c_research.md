# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/antiword/main_ros.c

RISC OS GUI entry point for `!Antiword`.

Responsibilities:

- Initializes DeskLib resources, event system, templates, choices window, iconbar icon, and menus.
- Creates per-document diagrams/windows via `pCreateTextWindow()`.
- Processes a Word file in `vProcessFile()`:
  - opens file,
  - gets size,
  - guesses Word version,
  - rejects RTF/WordPerfect/non-Word cases,
  - optionally sets RISC OS filetype,
  - creates diagram,
  - calls `bWordDecryptor()`,
  - verifies Drawfile diagram,
  - displays it.
- Handles iconbar menu actions, save menu selections, scale view, save drawfile, save text.
- Handles RISC OS `DATALOAD` / `DATAOPEN` messages and sends `DATALOADACK`.
- Enters infinite `Event_Poll()` loop after initialization and optional command-line file processing.

This file is platform orchestration only; all Word parsing and conversion are delegated to shared Antiword modules.
