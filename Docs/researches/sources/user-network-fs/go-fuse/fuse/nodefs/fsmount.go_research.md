## sources/user-network-fs/go-fuse/fuse/nodefs/fsmount.go

Purpose: nodefs mount metadata and open-file handle support for mounted inode subtrees.

Important APIs/types/functions: `openedFile` stores a registered regular file or open directory plus `WithFlags`. `fileSystemMount` stores mount/root/parent inodes, `Options`, `treeLock`, `openFiles`, debug flag, and connector. Methods include `mountName`, `setOwner`, `fillEntry`, `fillAttr`, `getOpenedFile`, `unregisterFileHandle`, `registerFileHandle`, and `negativeEntry`.

Control flow: raw open/create/opendir paths register `File` or `connectorDir` objects into the mount's handle map, flatten nested `WithFlags`, attach the file to the inode, and return handle 0 for handleless opens. Release paths unregister the handle and remove it from the inode's open-file slice. Entry/attr helpers apply timeout and owner options before returning protocol structs.

State and persistence: mount records, open file handles, tree locks, and timeout/owner options are in-memory mount-lifetime state. Backing persistence belongs to the node/file implementation.

Dependencies and integration: used by `FileSystemConnector.Mount`, `Unmount`, and `fsops` lookup redirection.

Risks and test signals: handleless-open handling, open-file slice removal, nested `WithFlags`, and negative entry timeouts are sensitive. Handle and fileless tests provide direct signals.
