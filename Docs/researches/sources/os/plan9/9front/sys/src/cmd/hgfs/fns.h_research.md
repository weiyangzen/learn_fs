# File Research: sources/os/plan9/9front/sys/src/cmd/hgfs/fns.h

Declares all `hgfs` helper APIs.

Key points:
- Hash helpers:
  - `Hfmt`, `hex2hash`, `hash2qid`, `fhash`, `readhash`
- Patch helpers:
  - `fcopy`, `fpatchmark`, `fpatch`
- Revlog decompression:
  - `funzip`
- Revlog operations:
  - `fmktemp`, `revlogopen`, `revlogupdate`, `revlogclose`, `revlogextract`, `revhash`, `hashrev`, `revlogopentemp`, `fmetaheader`
- Changelog metadata:
  - `loadrevinfo`
- Manifest tree operations:
  - `nodepath`, `mknode`, `loadfilestree`, `loadchangestree`, `closerevtree`
- Utility operations:
  - `hashstr`, `getworkdir`, `readfile`
- Ancestor finder:
  - `ancestor`

Dependencies and interactions:
- Included by `hgfs` implementation files.
- Provides module boundaries across parsing, revlog extraction, manifest trees, and 9P serving.

Research relevance:
- Compact map of the `hgfs` subsystem’s internal API.
