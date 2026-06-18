# sources/sync-backup/git-crypt/fhstream.hpp

Purpose: declares stream adapters `ofhstream` and `ifhstream` plus their underlying stream buffers for callback-backed handles.

Important APIs/types/functions: `ofhbuf`, `ofhstream`, `ifhbuf`, and `ifhstream`; callback signatures `size_t (*write_fun)(void*, const void*, size_t)` and `size_t (*read_fun)(void*, void*, size_t)`; deleted copy/assignment for buffers.

Control flow: constructors install custom buffers into standard stream base classes. Implementations handle overflow, sync, underflow, direct bulk I/O, and buffer switching.

State/persistence behavior: state is internal buffer memory and callback handle pointers. Destructors release buffers; `ofhbuf` destructor attempts to sync while ignoring exceptions.

Dependencies/integration: included by platform `Coprocess` headers to expose pipe streams as standard C++ iostreams.

Risks/test signals: destructor sync can hide final write errors unless callers explicitly sync/close. Tests should use fake callbacks to verify buffering and partial I/O behavior deterministically.
