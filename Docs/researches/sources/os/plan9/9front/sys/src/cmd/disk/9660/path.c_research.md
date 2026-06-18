# File Research: sources/os/plan9/9front/sys/src/cmd/disk/9660/path.c

ISO 9660 path table generation and descriptor patching.

Key behavior:
- Writes little-endian and big-endian path tables at the end of the image after directories are finalized.
- Uses the just-written path table as a breadth-first queue while reading directory records from the image.
- Tracks directory lengths separately because path table records do not store them.
- `writepathtablepair` writes both endian variants and patches descriptor path size and locations.
- `writepathtables` applies this to the primary descriptor and optional Joliet descriptor.

Notable dependencies:
- `Creadblock`, `Crdpath`, `writepath`, `setpathtable`, and directory record structures.

Research notes:
- The file includes a warning not to pad path table entries across block boundaries, based on observed Windows behavior.
