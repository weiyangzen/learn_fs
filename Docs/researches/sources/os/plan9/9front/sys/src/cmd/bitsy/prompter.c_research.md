# File Research: sources/os/plan9/9front/sys/src/cmd/bitsy/prompter.c

This is a touch-friendly prompt/file editor with an on-screen keyboard and optional scribble area.

Behavior:
- Reads an input file into up to 24 editable lines.
- Builds text entry controls for as many lines as fit above the keyboard.
- Routes physical keyboard events to text entries and on-screen keyboard/scribble events into the keyboard channel.
- Exits on mouse button bit `0x20` or Escape.
- Writes non-trailing-empty lines back to the same file.

Notable implementation details:
- Uses two control sets: one for keyboard/scribble, one for text entries.
- `mousemux` routes mouse events by y-coordinate split at `kbdy`.
- `resizemux` forwards resize events to both control sets.
- `-n` disables scribble.

Risks and caveats:
- Reads the whole file based on `Dir.length`.
- Only visible/managed lines are written back, bounded by the calculated `Nline`.
