# File Research: sources/os/plan9/9front/sys/src/cmd/aux/antiword/main_ros.c

This file is the RISC OS GUI entry point for `!Antiword`.

Key routines:
- GUI/menu handlers: `bBarInfo`, `vBarInfoSetText`, `bMouseButtonClick`, `bAutoRedrawWindow`, `bSaveSelect`, `bMenuSelect`, `bMenuClick`.
- Window setup: `pCreateTextWindow(...)`, `vTemplates()`, `vInitialise()`.
- File processing: `vProcessFile(...)` opens a file, identifies Word version, optionally sets filetype, creates a diagram, runs `bWordDecryptor`, verifies drawfile data, and shows the diagram.
- Messaging: `vSendAck(...)`, `bEventMsgHandler(...)`.
- `main(...)` initializes the GUI, reads options, optionally opens one file, then enters the event loop.

Important behavior:
- Handles RISC OS DataLoad/DataOpen messages and Closedown.
- Creates per-document save menus for scale view, drawfile save, and text-only save.
- Uses DeskLib event claims and RISC OS templates/resources.

Dependencies:
- DeskLib Dialog/Event/Menu/Template/Window APIs, drawfile verifier, filetype helpers, option reader, Word detector/decryptor, diagram/window helpers.

Role in antiword:
- RISC OS application shell around the shared Word decoding/rendering core.
