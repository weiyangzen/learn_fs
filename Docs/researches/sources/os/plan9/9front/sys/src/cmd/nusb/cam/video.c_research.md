# File Research: sources/os/plan9/9front/sys/src/cmd/nusb/cam/video.c

This file implements the UVC video streaming path. It manages a pool of `VFrame` objects, reads isochronous/bulk video payloads from the selected endpoint, reconstructs complete raw frames, converts them to Plan 9 RGB image data, and services pending 9P video reads.

Frame queues are split into free and active lists protected by `Cam.qulock`. `grabframe()` obtains a free frame or recycles an inactive active-list frame, while `pushframe()` appends a completed frame and wakes deferred reads. `videoread()` either returns the next bytes of an active frame, queues the 9P request if no frame is available, or returns a zero-length delimiter in frame mode after a complete frame has been consumed. `videoflush()` removes an interrupted queued read.

The only built-in pixel converter is YUY2. `yuy2convert()` transforms packed YUY2 into a Plan 9 `b8g8r8` image buffer with a 60-byte image header. `getconverter()` matches a UVC GUID against the converter table and reports unknown format GUIDs.

`cvtproc()` is the streaming worker. It reads endpoint packets, tracks UVC frame-id toggles in the payload header, accumulates payload bytes until a full raw frame is present, converts the frame, and pushes it to readers. On abort or read failure it frees frame lists, closes the endpoint, restores the streaming interface alternate setting, and clears active state.

`videoopen()` validates the selected frame descriptor and converter, performs UVC probe/commit negotiation, selects an alternate endpoint setting with sufficient bandwidth in `selbw()`, opens endpoint data, allocates the frame pool, and starts `cvtproc()`. `videoclose()` interrupts the converter process by setting the abort flag and sending a thread interrupt.
