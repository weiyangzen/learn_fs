## sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/stream/TestDirstreamClientHandler.java

Purpose: Tests `DirstreamClientHandler` parsing of directory streaming protocol chunks and validation of malformed file headers.

Important APIs/types/functions: `DirstreamClientHandler.doRead`, `isAtTheEnd`, `DirectoryServerDestination`, Netty `ByteBuf`, and invalid-format parameter provider.

Control flow: Tests stream messages containing file-size/name headers, content bytes, and `END`, split across header boundaries, inside headers, second headers, and content. Valid cases assert written file contents and end state. Invalid cases pass malformed headers and expect `IllegalArgumentException` containing "Invalid file name format".

State and persistence behavior: Writes streamed file contents into a temporary destination directory.

Dependencies and integration points: Covers client-side protocol parser used by `StreamingClient` and directory destination writer.

Risks and test signals: Strong parser boundary coverage. It validates header format but not path traversal or nested directory names in this file.
