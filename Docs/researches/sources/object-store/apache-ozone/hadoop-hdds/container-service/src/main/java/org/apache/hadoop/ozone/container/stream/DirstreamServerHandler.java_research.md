# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/stream/DirstreamServerHandler.java

Purpose: Netty server handler for the custom directory-stream protocol, reading a requested ID and writing a sequence of file headers and file contents.

Important APIs and functions: `channelRead` reads the first newline-terminated request ID, asks `StreamingSource.getFilesToStream`, and calls `writeOneElement`. `writeOneElement` writes a header `<fileSize> <logicalName>\n`, then a Netty `ChunkedFile`, then either recursively streams the next entry or writes `END_MARKER` and closes the channel. `exceptionCaught` writes an `ERR:` line if possible and closes the channel.

Control flow and state: `headerProcessed` ensures only the first request header is interpreted. File writes are chained through `ChannelFuture` listeners to avoid sending the next file before the current file write is submitted/completed.

Dependencies and integration: installed by `StreamingServer` after `ChunkedWriteHandler`. It consumes `StreamingSource` and produces the format parsed by `DirstreamClientHandler`.

Risks and test signals: empty source maps cause `entriesToWrite.get(0)` failure. Request header parsing for fragmented headers is weak because it does not accumulate partial data across reads. Tests should cover empty directories, fragmented request ID, multiple files, chunked write failure, error response formatting, and end marker newline expectations.
