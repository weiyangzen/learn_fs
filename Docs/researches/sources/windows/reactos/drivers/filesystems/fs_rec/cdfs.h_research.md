# File Research: sources/windows/reactos/drivers/filesystems/fs_rec/cdfs.h

Minimal ISO-9660 volume descriptor header for the CDFS recognizer. `VD_HEADER` contains the descriptor type byte, five-byte identifier, and version byte. Constants define the primary descriptor offset `32768`, expected identifier `CD001`, identifier length, primary descriptor type `1`, and volume descriptor version `1`. The header intentionally contains only the signature fields needed for recognition.
