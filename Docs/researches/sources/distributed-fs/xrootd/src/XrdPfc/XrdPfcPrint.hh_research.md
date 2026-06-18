# sources/distributed-fs/xrootd/src/XrdPfc/XrdPfcPrint.hh

## Purpose
Declares the `Print` helper used by the `pfc_print` command-line utility. It encapsulates OSS access, output units, verbosity, JSON formatting, indentation, and recursive metadata printing.

## Important APIs, Types, and Functions
- Constructor `Print(XrdOss* oss, char u, bool v, bool j, int i, const char* path)` immediately prints the requested path.
- Private `isInfoFile`, `printFileJson`, `printFile`, and `printDir` implement dispatch and output.
- Members store OSS handle, environment, unit shift/width/name, format flags, JSON indent, and OSS user.

## Control Flow
The constructor is the entry point and dispatches based on whether the path is a `.cinfo` file. Directory recursion and file formatting are implementation details.

## State and Persistence Behavior
State is command-runtime only. No persistent data is written by this class.

## Dependencies and Integration Points
Depends on `XrdOucEnv`, forward-declared `XrdOss`, and `XrdOssDF`. It is coupled to `Info` in the implementation.

## Risks and Test Signals
Risks are limited to utility behavior: constructor side effects, fixed OSS user `"nobody"`, and suffix handling. Tests should instantiate against a fake or test OSS tree and validate both JSON and text outputs.
