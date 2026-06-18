# File Research: sources/virtualization/guestfs-tools/test-data/phony-guests/make-windows-img.sh

Shell generator for a minimal Windows-like disk image.

Key behavior:
- Checks whether libguestfs supports NTFS tooling; if not, touches empty `windows.img` and exits successfully with a warning.
- Creates a 2G MBR disk with bootloader and root NTFS partitions.
- Writes disk ID bytes at offset `0x01b8`.
- Creates Windows system directories.
- Uploads generated `SOFTWARE` and `SYSTEM` registry hives.
- Uploads `bin-win32.exe` as `cmd.exe`.
- Creates `Program Files` and `autoexec.bat`.
- Renames temporary output to `windows.img`.

Research notes:
- Produces enough Windows structure for inspection and registry tests when NTFS support exists.
