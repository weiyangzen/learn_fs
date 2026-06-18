# File Research: sources/windows/reactos/ntoskrnl/mm/ARM3/sysldr.c

ReactOS ARM3 kernel system loader implementation for loading, relocating, linking, protecting, paging, querying, and unloading kernel PE images.

Key responsibilities:
- Maintains loaded-module globals: `PsLoadedModuleList`, `MmLoadedUserImageList`, `PsLoadedModuleResource`, `PsLoadedModuleSpinLock`, `MmSystemLoadLock`, `PsNtosImageBase`, driver page counters, and kernel section PTE ranges.
- Loads an image section into system space through `MiLoadImageSection()`: maps the SEC_IMAGE view in the system process, reserves system PTEs, allocates PFN-backed pages, copies the mapped image, and unmaps the temporary view.
- Implements PE export lookup with `NameToOrdinal()`, `RtlpFindExportedRoutineByName()`, and `RtlFindExportedRoutineByName()`.
- Handles loader DLL callbacks through `MmCallDllInitialize()` and `MiCallDllUnloadAndUnloadDll()`.
- Tracks dependency references with `MiResolveImageReferences()`, `MiDereferenceImports()`, and `MiClearImports()`.
- Snaps import thunks with `MiSnapThunk()`, including ordinal imports, named imports, and recursive forwarder resolution.
- Initializes boot-loaded module bookkeeping with `MiInitializeLoadedModuleList()`, `MiBuildImportsForBootDrivers()`, `MiReloadBootLoadedDrivers()`, and `MiUpdateThunks()`.
- Frees discardable/init code ranges through `MiFindInitializationCode()`, `MiFreeInitializationCode()`, and `MmFreeDriverInitialization()`.
- Locates and modifies kernel resource/pool/sysPTE sections with `MiLocateKernelSections()`, `MmChangeKernelResourceSectionProtection()`, and `MmMakeKernelResourceSectionWritable()`.
- Applies per-section image protection through `MiWriteProtectSystemImage()` and `MiSetSystemCodeProtection()`.
- Provides public loader-facing APIs: `MmLoadSystemImage()`, `MmUnloadSystemImage()`, `MmCheckSystemImage()`, `MmPageEntireDriver()`, `MmResetDriverPaging()`, and `MmGetSystemRoutineAddress()`.

Important behavior:
- `MmLoadSystemImage()` is the central load path: parses base and directory names, handles optional name prefixes, deduplicates against `PsLoadedModuleList`, opens and validates the file, creates a section, copies it into ARM3 system PTE space, relocates it, creates an `LDR_DATA_TABLE_ENTRY`, resolves imports, write-protects sections, initializes the security cookie, sends image-load notifications, loads symbols when requested, and enables driver paging.
- Import validation rejects user-mode imports such as `ntdll`, `kernel32`, `user32`, `gdi32`, and mixed win32k/non-win32k import patterns for GDI-style drivers.
- Core imports from `ntoskrnl`, `hal`, and `win32k` are treated specially and not reference-counted like normal dependent DLLs.
- Boot import reconstruction scans already-fixed IAT entries to infer dependency ownership and stores either no imports, a tagged single import pointer, or a `LOAD_IMPORTS` array.
- `MiReloadBootLoadedDrivers()` moves eligible boot drivers into ARM3-controlled system PTE space, reuses existing PFNs, relocates the copied image, updates loader entries, and patches thunks in other boot modules.
- `MmUnloadSystemImage()` decrements load counts and cleans loader metadata and imports, but the actual driver image memory free is explicitly marked FIXME and logged as leaked.
- `MmGetSystemRoutineAddress()` searches only `ntoskrnl.exe` and `hal.dll` exports.
- Session image loading, large-page driver mapping, `MmResetDriverPaging()`, and actual driver paging are incomplete or disabled.

Dependencies:
- Heavy PE/COFF dependency: NT headers, section headers, data directories, import/export descriptors, load config, checksums, relocations, IATs, and security cookies.
- Uses ARM3 memory-manager primitives: system PTE reservation, PFN allocation/init, PTE writes, TLB flushes, system pageable VM deletion, PTE-to-address conversion, and physical/session address predicates.
- Uses object manager, section manager, file APIs, loader support, process attach APIs, resources, spin locks, mutants, debug symbol APIs, and image-load notify callbacks.
- Shares module-list and loader-entry semantics with the executive, I/O manager, debugger, and driver initialization paths.

Notable risks:
- `MiLoadImageSection()` maps the section before reserving system PTEs; on `MiReserveSystemPtes()` failure it returns without visibly unmapping the temporary mapped view in this file.
- Several later `MmLoadSystemImage()` failure paths after copying/relocating the image drop to cleanup without visibly releasing the ARM3 system PTE allocation or copied image pages.
- Actual unload still leaks the mapped driver image.
- Session loading is detected in multiple places but not implemented.
- Large-page mapping always returns unsupported after registry/list checks.
- Driver paging is compiled out because the page-fault path is noted as broken.
- Forwarded exports are supported by import snapping but deliberately not by public `RtlFindExportedRoutineByName()`.
- Import-list encoding uses special sentinel pointers and low-bit tagging, so cleanup and reference handling depend on strict pointer interpretation.
