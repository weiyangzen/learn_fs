# File Research: sources/windows/windows-driver-samples/filesys/miniFilter/NameChanger/nc.h

This is the shared interface and data-model header for the NameChanger minifilter. It defines allocation tags, compatibility function pointer types, path/mapping structures, per-instance and per-handle contexts, directory-entry offset helpers, global data, and cross-module function declarations.

Core structures:
- `NC_MAPPING_PATH`: precomputed full, volume, parent, final-component, and volumeless names plus component counts.
- `NC_MAPPING_ENTRY`: long-name and short-name mapping path pair.
- `NC_MAPPING`: real mapping plus user mapping.
- `NC_PATH_OVERLAP`: flags describing whether a path is an ancestor, parent, exact match, inside mapping, or peer.
- `NC_INSTANCE_CONTEXT`: per-volume mapping plus attached filesystem type.
- `NC_DIR_QRY_CONTEXT`: per-handle directory enumeration cache, injection entry, search string, information class, and outstanding flag.
- `NC_DIR_NOT_CONTEXT`: per-handle directory notification forwarding/merge state.
- `NC_FIND_BY_SID_CONTEXT`: state for `FSCTL_FIND_FILES_BY_SID`, including real handle and buffered results.
- `NC_STREAM_HANDLE_CONTEXT`: shared per-handle lock plus directory query, notification, and find-by-SID state.

The header also defines `DIRECTORY_CONTROL_OFFSETS`, used to generically inspect and edit the multiple directory information buffer formats returned by Windows filesystems.

Compatibility declarations abstract OS-version differences:
- `NcReplaceFileObjectName`
- `NcQueryDirectoryFile`
- `NcCreateFileEx2`
- `NcGetNewSystemBufferAddress`

The function declaration sections define the module boundaries:
- `nchelper.c`: name querying, resource allocation, create helper, cancel completion, exception filter.
- `ncmapping.c`: mapping initialization, build, teardown.
- `ncinit.c`: registry mapping initialization.
- `ncpath.c`: path comparison, construction, final-component parsing.
- `nccontext.c`: context allocation/close routines.
- `nccreate.c`: create redirection.
- `ncnameprov.c`: generated and normalized names.
- `ncoffsets.c`: directory information buffer accessors/mutators.
- `ncdirenum.c`: directory enumeration injection/filtering.
- `ncdirnotify.c`: directory notification forwarding.
- `ncfileinfo.c`: file information name fixups and set-information guards.
- `ncfsctrl.c`: FSCTL result/name fixups.

Notable details:
- The driver relies on precomputed mapping paths rather than reparsing mapping configuration for every operation.
- Per-handle locking uses an `ERESOURCE` allocated in the stream handle context.
- Directory enumeration and notifications share the stream handle context but keep separate subcontexts.
- Some declarations are duplicated for `NcIsMappingZeroed` and `NcInitMapping`; this is harmless but redundant.
