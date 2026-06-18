# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/stream/DirstreamClientHandler.java

Purpose: Netty inbound handler that receives the custom directory-stream protocol and writes files to a `StreamingDestination`.

Important APIs and functions: `channelRead` casts to `ByteBuf`, calls `doRead`, and releases the buffer. `doRead` alternates between header mode and data mode. Headers are newline-terminated strings in the form `<size> <filename>`; the handler parses size, maps filename to a destination path, creates parent directories, opens a `RandomAccessFile`, and then copies exactly `size` bytes to its `FileChannel`. Extra bytes in a buffer after a file completes are processed recursively. `isAtTheEnd` checks whether the last header equals server `END_MARKER`.

Control flow and state: state fields track header/data mode, accumulated header text, open output file/channel, and remaining bytes. Channel unregister and exception paths close open files.

Dependencies and integration: used by `StreamingClient`. It relies on `DirstreamServerHandler.END_MARKER` and Netty buffer reference counting.

Risks and test signals: the stated protocol comment disagrees with parsing order in one place; actual parsing is size then filename. Tests should cover split headers, multiple files in one buffer, zero-size end marker, malformed headers, destination parent null, partial transfer close, and resource cleanup.
