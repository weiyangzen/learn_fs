<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/share/RingBuffer.java -->
# sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/share/RingBuffer.java

Purpose: Fixed-size circular byte buffer used by FileOutputStream's ByteChunkProvider.

Important APIs/types/functions: write(byte[], int, int), write(int), read(byte[]), maxSize(), size(), isFull(), isFull(int), and isEmpty().

Control flow: write validates source length and available capacity, copies bytes either contiguously or wrapped around the end, advances writeIndex modulo buffer length, and increments size. read copies up to requested chunk length from readIndex with wrap support, advances readIndex, and decrements size.

State and persistence behavior: Maintains byte array, writeIndex, readIndex, and size only in memory.

Dependencies and integration points: Package-private helper for FileOutputStream.ByteArrayProvider.

Risks: Not thread-safe. Error message says accomodate misspelled but harmless. No constructor validation for zero/negative maxSize; modulo by zero would fail later. read(byte[0]) returns zero.

Test signals: Write/read exact capacity, wraparound write/read, overflow write exception, source bounds exception, isFull(len) exception for too-large len, and zero-size construction behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smbj/src/main/java/com/hierynomus/smbj/share/RingBuffer.java -->
