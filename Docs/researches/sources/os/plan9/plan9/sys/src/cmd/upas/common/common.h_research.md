# File Research: sources/os/plan9/plan9/sys/src/cmd/upas/common/common.h

- Role: Shared upas common header aggregating system wrappers, mail header regex globals, mailbox constants, process stream types, and utility prototypes.
- Key content: `IS_HEADER`, `IS_TRAILER`, mailbox type constants, `stream`, `process`, process control APIs, append/copy APIs, and auxiliary string/path APIs.
- Integration: Included by alias, filterkit, and common source files.
- Risks/notes: Includes broad global state and prototypes; modules are tightly coupled through this header.
