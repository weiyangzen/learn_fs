# File Research: sources/os/plan9/9front/sys/src/cmd/camv.c

Purpose: Graphical camera viewer and control utility for a Plan 9 camera device directory.

Key points:
- Opens `<cam-device>/ctl` read-write and `<cam-device>/video` for image frames.
- Reads control lines into a linked list of `Control` records containing unit, control name, value, and optional info.
- Creates a draw window and centers frames read with `readimage`.
- Uses a video process that reopens the video stream on read failure.
- Handles resize events in a separate thread.
- Right mouse menu offers quit.
- Middle mouse menu lists controls, prompts for a new value with `enter`, writes quoted control update commands, then refreshes controls.

Dependencies and interactions:
- Uses Plan 9 thread, draw, mouse, keyboard, and bio libraries.
- Expects camera device files with `ctl` and `video` interfaces.
- Uses `quotefmtinstall` for quoted control writes.

Research notes:
- UI is simple but concurrent: draw locking is used around display updates and mouse menu interactions.
- `readctls` appends newly allocated controls after seeking the control stream, and `freectls` is used before refresh.
