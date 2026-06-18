<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/Enums/FileSystemInformation/DeviceType.cs -->
# sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/Enums/FileSystemInformation/DeviceType.cs

## Purpose
Defines the wire-level `DeviceType` enumeration used by SMBLibrary to name protocol constants without scattering raw integer literals through packet and file-store code.

## Important APIs, Types, And Functions
The exported enum values include Beep = 0x0001, CDRom = 0x0002, CDRomFileSystem = 0x0003, Controller = 0x0004, DataLink = 0x0005, DFS = 0x0006, Disk = 0x0007, DiskFileSystem = 0x0008, FileSystem = 0x0009, ImportPort = 0x000A, Keyboard = 0x000B, MailSlot = 0x000C, MidiIn = 0x000D, MidiOut = 0x000E, Mouse = 0x000F, MultiUNCProvider = 0x0010, NamedPipe = 0x0011, Network = 0x0012, NetworkBrowser = 0x0013, NetworkFileSystem = 0x0014, Null = 0x0015, ParallelPort = 0x0016, PhysicalNetcard = 0x0017, Printer = 0x0018, Scanner = 0x0019, SerialMousePort = 0x001A, SerialPort = 0x001B, Screen = 0x001C, Sound = 0x001D, Streams = 0x001E, Tape = 0x001F, TapeFileSystem = 0x0020, Transport = 0x0021, Unknown = 0x0022, Video = 0x0023, VirtualDisk = 0x0024, WaveIn = 0x0025, WaveOut = 0x0026, PS2Port = 0x0027, NetworkRedirector = 0x0028. The underlying type and numeric assignments are taken directly from SMB/NT/Win32 protocol contracts in the source.

## Control Flow
There is no runtime branch logic in this file. Control flow appears when parsers cast little-endian integers into this enum and writers cast enum values back to their protocol integer width.

## State And Persistence Behavior
The enum has no mutable state or persistence. Its values persist only as serialized fields in SMB, DFS, NT file-store, security, or filesystem information packets.

## Dependencies And Integration Points
Integrated by the client, server, NT file-store structures, and SMB1/SMB2 packet serializers that need stable protocol values.

## Risks
The main risk is numeric drift from the Microsoft protocol constants. Flag enums also need callers to mask and combine values carefully so unknown bits are not silently interpreted as supported behavior.

## Test Signals
Useful tests are compile-time references from serializers plus round-trip packet tests that verify the exact integer values on the wire, including combinations for flag enums.
<!-- END_FILE_RESEARCH: sources/user-network-fs/smblibrary/SMBLibrary/NTFileStore/Enums/FileSystemInformation/DeviceType.cs -->
