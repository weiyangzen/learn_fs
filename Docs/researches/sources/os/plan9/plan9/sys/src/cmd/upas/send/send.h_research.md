# File Research: sources/os/plan9/plan9/sys/src/cmd/upas/send/send.h

Read fully: 114 lines, 3580 bytes. SHA-256 prefix: `b47778fb26f278ce`.

This is the shared private interface for `upas/send`. It defines recipient grouping limits (`MAXSAME`, `MAXSAMECHAR`), the `d_status` delivery-state enum, destination records, message records, global flags, and function prototypes used across the sender implementation.

`dest` models one delivery target plus rewrite/translation output, same-command recipient coalescing, parent translations, process status, and authorization state. `message` tracks parsed sender/reply/date/body/temp-file data, discovered RFC822 headers, MIME status, size, and attachment boundary.

Integration: included by send-side modules such as local delivery, rewriting, authorization, translation, logging, forwarding checks, and refusal reporting. It binds the module contracts tightly around Plan 9 `String`, `Biobuf`, `process`, and upas common helpers.

Risk notes: the enum values and struct fields are behavioral contracts across many C files. Recipient coalescing limits are explicitly SMTP/interoperability driven; changing them can affect command lengths and remote mail-system behavior.
