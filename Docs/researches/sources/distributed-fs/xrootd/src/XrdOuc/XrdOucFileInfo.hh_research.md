# sources/distributed-fs/xrootd/src/XrdOuc/XrdOucFileInfo.hh

## Purpose
Declares the file-resource description object used to collect alternate URLs, digests, logical names, target names, size, and protocol availability.

## Important APIs, Types, And Functions
Public API includes `AddDigest`, `AddUrl`, `AddFileName`, `AddLfn`, `AddProtocol`, `GetDigest`, `GetLfn`, `GetTargetName`, `GetSize`, `GetUrl`, `HasProtocol`, and `SetSize`. `nextFile` is a public link for chaining multiple file descriptions. Private members are digest and URL list heads/iterators, strings, size, and protocol list.

## Control Flow
Callers populate the object with metadata, iterate URLs and digests until null, and may chain objects through `nextFile`. Constructor optionally sets the LFN and initializes size to `-1` as unknown.

## State And Persistence
The object owns duplicated strings and helper nodes until destruction. It does not persist data outside the process.

## Dependencies And Integration Points
Includes C string/allocation headers and `<string>`. It is a utility contract for modules that need to return file-location metadata independent of a specific protocol.

## Risks And Test Signals
Risks include non-copy-safe raw ownership because no copy constructor/assignment is defined, public link ownership ambiguity, and iterator state embedded in the object. Test signals are destructor memory checks, unknown-size handling, and API users avoiding accidental copies.
