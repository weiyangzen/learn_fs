<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/libsmb2/lib/ps2/irx_imports.h -->
# sources/user-network-fs/libsmb2/lib/ps2/irx_imports.h

## Purpose

`irx_imports.h` is a PS2 IOP module convenience header. It centralizes IRX import headers needed by the SMB2MAN PS2 build so source files can include one local header for kernel, IO, networking, memory, thread, and semaphore APIs.

## Important APIs, Types, And Functions

The file declares no functions or data. Its public surface is the include guard `IOP_IRX_IMPORTS_H` and inclusions of `<irx.h>`, `<intrman.h>`, `<ioman.h>`, `<ps2ip.h>`, `<sifman.h>`, `<stdio.h>`, `<sysclib.h>`, `<sysmem.h>`, `<thbase.h>`, and `<thsemap.h>`.

## Control Flow

There is no runtime control flow. At compile time, it pulls in PS2SDK import definitions required for IRX linking and module symbol resolution.

## State And Persistence Behavior

No state is stored or persisted. Its only effect is on compilation and module import visibility.

## Dependencies And Integration Points

It depends on PS2SDK headers and is intended for IOP/IRX builds, not host builds. It integrates with PS2-specific libsmb2 files such as `smb2man.c` and `smb2_fio.c` when they need IRX service declarations.

## Risks And Edge Cases

The header can hide accidental dependency creep because including it imports many subsystems at once. It also uses `<ioman.h>` while `smb2_fio.c` uses `iomanX.h`, so API mismatches between IOMAN variants should be watched in PS2 build configurations.

## Test Signals

The useful signal is a PS2SDK IRX build that compiles with strict include paths and no missing import stubs. Also verify the header is not included by non-PS2 targets.
<!-- END_FILE_RESEARCH: sources/user-network-fs/libsmb2/lib/ps2/irx_imports.h -->
