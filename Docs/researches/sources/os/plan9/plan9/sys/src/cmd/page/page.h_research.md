# File Research: sources/os/plan9/plan9/sys/src/cmd/page/page.h

Shared header for the `page` program. It defines the `Document` interface: document name, page count, forward-only flag, page-name callback, draw-page callback, optional add/remove callbacks, backing `Biobuf`, and backend-specific `extra`.

It declares backend initializers for PostScript, PDF, graphics, troff, DVI, and Microsoft Office conversion, plus viewer, cache, rotation/resampling, Ghostscript, temporary input, window, label, and utility helpers.

`GSInfo` records Ghostscript command/data fds, reader buffer, process id, and rendering PPI. The header also exposes global configuration flags such as `chatty`, `ppi`, `reverse`, antialias bits, resizing, true-color mode, and stdin fd.

The final macros intentionally map draw operations back to older draw calls because new draw operators were not reliable across drawterm/vncs and some kernel paths.
