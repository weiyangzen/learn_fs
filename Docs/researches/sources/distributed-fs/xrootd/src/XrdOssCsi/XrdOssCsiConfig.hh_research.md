# sources/distributed-fs/xrootd/src/XrdOssCsi/XrdOssCsiConfig.hh

Purpose: declares configuration and tag-path naming rules for XrdOssCsi. `TagPath` maps client-visible data paths to hidden checksum tag paths and detects tag-file paths that should be hidden or rejected.

Important APIs/types: `TagPath::isTagFile()` detects either prefix-tree tag files or suffix-based tag files when prefix is empty. `SetPrefix()` validates empty or absolute prefix. `makeBaseDirname()` maps data directories to tag directories; `matchPrefixDir()`/`getPrefixName()` support directory listing suppression; `makeTagFilename()` maps data files to tag files. `simplePath()` normalizes slashes and leading/trailing slash behavior. `XrdOssCsiConfig` exposes `Init()`, `fillFileHole()`, `xrdtSpaceName()`, `allowMissingTags()`, `disablePgExtend()`, `disableLooseWrite()`, and public `tagParam_`.

State/control: defaults are prefix `/.xrdt`, suffix `.xrdt`, fill file holes enabled, tag space `public`, missing tags allowed, pg extension enabled, and loose writes enabled. Path mapping preserves whether the caller gave an absolute path when constructing relative tag filenames.

Risks/test signals: path normalization is central and easy to regress; prefix-empty mode changes hiding from prefix tree to suffix matching. Tests should cover absolute/relative paths, double/trailing slashes, root path, empty prefix, prefix directory listing suppression, invalid relative prefix, and tag filename creation for nested files.
