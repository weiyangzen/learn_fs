# File Research: sources/windows/windows-driver-samples/filesys/miniFilter/scanner/user/scanUser.c

User-mode scanner service sample that receives scan requests and replies to the minifilter.

Key responsibilities:
- Connects to `\\ScannerPort`.
- Associates the filter communication port with an I/O completion port.
- Starts configurable worker threads and posts configurable outstanding `FilterGetMessage` requests per thread.
- Scans received buffers for the literal byte string `"foul"`.
- Replies with `SafeToOpen = FALSE` when the string is found.

Important behavior:
- Defaults to 5 outstanding requests per thread and 2 worker threads; allows 1 to 64 threads.
- `ScannerWorker` dequeues overlapped completions, identifies the containing `SCANNER_MESSAGE`, scans `Notification.Contents`, replies with `FilterReplyMessage`, clears the `OVERLAPPED`, and reposts `FilterGetMessage`.
- Multiple outstanding messages can complete in any order, so each message embeds its own `OVERLAPPED`.
- The main thread waits for workers and exits when workers fail or the port disconnects, commonly because the filter unloaded.

Dependencies and risks:
- Depends on `fltuser.h`, `scanuk.h`, and `scanuser.h`.
- `ScanBuffer` is an intentionally simple sample search algorithm, not production malware scanning.
- If `BufferSize` is smaller than the search string length, the pointer arithmetic in the loop condition is fragile sample code.
- There is no explicit graceful shutdown command; normal termination depends on port closure/error.
