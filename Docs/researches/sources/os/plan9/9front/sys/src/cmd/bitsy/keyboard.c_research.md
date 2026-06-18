# File Research: sources/os/plan9/9front/sys/src/cmd/bitsy/keyboard.c

This is a graphical on-screen keyboard and optional scribble input tool for Bitsy/touch environments.

Major responsibilities:
- Creates keyboard and scribble controls.
- Writes selected runes to `/dev/kbdin` or `#r/kbdin`, falling back to stdout.
- Optional window list mode (`-w`) shows rio windows and can raise/select them.
- Optional layout flags choose scribble side or keyboard-only mode.
- Mouse button bit `0x20` toggles hide/unhide through `/dev/wctl`.

Notable implementation details:
- Uses Plan 9 control library widgets: keyboard, scribble, text buttons, boxbox.
- Polls `/dev/wsys` to build window-button list.
- Handles resize by recalculating rectangles for keyboard, scribble, and window list.
- Uses channels for keyboard events, control events, and timer refresh.

Risks and caveats:
- Contains an empty infinite `watchproc` that is not used.
- Several resources and layout sizes are hardcoded for small-screen devices.
- `namectlimage(colors[Shade], "keymask")` appears where `colors[Mask]` would be expected.
