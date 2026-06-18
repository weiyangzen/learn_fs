# sources/user-network-fs/rclone/cmd/ncdu/ncdu.go

Purpose: implements interactive terminal UI for exploring remote disk usage, modeled after ncdu.

Important APIs/types: Cobra `commandDefinition`; `helpText`; `UI` state struct; drawing helpers (`Print`, `Line`, `Box`, `Draw`); navigation/delete/sort methods; `ncduSort`; `NewUI`; `scan`; `Run`; `key`.

Control flow: command creates source Fs and runs `NewUI(fsrc).Run()`. `Run` initializes tcell, redirects logs into a bounded in-memory buffer to avoid screen corruption, starts a background scanner, and selects over root, scan errors, update notifications, and keyboard events. Drawing computes per-entry attrs, flags unread/error/unknown-size/empty dirs, optional graph/count/average/modtime columns, and popup boxes. Deletes are synchronous after confirmation using `operations.DeleteFile` or `operations.Purge`, then mutate the in-memory scan tree.

State/persistence: UI keeps cursor positions, sort flags, selections, scan cancel function, and current tree. It can permanently delete remote files/directories. Dependencies include tcell, clipboard, runewidth/uniseg, scan package, operations. Risks: synchronous deletes block UI, scan/update races with UI tree reads, selection keyed by entry string, and terminal/log redirection edge cases. Test signal is mostly scan package tests; UI itself is not directly unit-tested.
