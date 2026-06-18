# File Research: sources/os/plan9/plan9/sys/src/cmd/abaco/page.c

Page lifecycle, loading, image fetching, rendering, selection, scrolling, and refresh handling for Abaco.

Key responsibilities:
- Loads child frames recursively from libhtml `Kidinfo`.
- Fetches and decodes images through webfs plus external image filters (`gif`, `jpg`, `png`, `ppm`, optional `resample`).
- Maintains a global cached image list with reference counts.
- Opens URLs through `urlopen`, reads response bodies, converts charset, parses HTML/plain text, fixes text, loads frames/images, and updates page state.
- Spawns page-loading work in a separate proc.
- Closes pages, child pages, layouts, images, docs, and URL/title state.
- Renders layouts and child frames, draws scrollbars, and redraws page backing images.
- Implements page selection, double-click, hit testing, mouse dispatch, key dispatch, snarfing, refresh scheduling, and meta-refresh.

Dependencies:
- Uses `urlopen`, `convert`, `parsehtml`, `laypage`, `laydraw`, `loadimages`, `addrefresh`, `flushrefresh`, `winaddhist`, and Plan 9 proc/thread APIs.
- Uses external image conversion commands through `execproc`.

Notable risks:
- Network/body loading accumulates full response contents in memory before parsing.
- Image filters are shell commands, so command strings and available tools matter.
- Page loading is asynchronous and relies on flags such as `loading`, `changed`, and `aborting`.
