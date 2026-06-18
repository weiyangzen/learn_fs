# sources/user-network-fs/rclone/cmd/help.go

Purpose: defines the root Cobra command and help subcommands for rclone. It centralizes usage templates, global flag registration, backend help rendering, and command traversal/completion setup.

Important APIs/types/functions: `Root`, `GeneratingDocs`, `helpCommand`, `helpFlags`, `helpBackends`, `helpBackend`, `runRoot`, `setupRootCommand`, `traverseCommands`, `showBackends`, `showBackend`, and templates `usageTemplate`, flag templates, and `docFlagsTemplate`. It registers config/filter/rc/log global flags and attaches Cobra template functions that group flags.

Control flow: `setupRootCommand` adds globals, usage templates, help commands, flag filters, and valid-args functions recursively. `runRoot` prints version or usage and maps missing commands to `errorCommandNotFound`. Backend helpers enumerate registered backends, sort display rows, and print option metadata.

State/persistence: package-level filter state controls help output; `PersistentPostRun` logs final version/args and runs `atexit`. Dependencies include rclone config/filter/log/rc flag registries and Cobra. Risks include template/filter global state carrying across generated-doc runs. Test signals likely come from command/docs tests outside this file.
