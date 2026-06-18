# File Research: sources/os/bsd/dragonflybsd/sys/kern/tty_cons.c

## Summary
Implements the logical `/dev/console` device and physical console selection/forwarding. It probes console drivers, attaches the selected console, intercepts open/close on the physical console, and forwards normal console operations.

## Main Responsibilities
- Selects the best `struct consdev` from `cons_set` during `cninit`.
- Completes console attachment in `cninit_finish` by intercepting the physical device ops.
- Creates `/dev/console` through `cn_drvinit`.
- Implements console muting via `kern.consmute`, including dynamic open/close of the physical device.
- Forwards `/dev/console` read/write/ioctl/kqueue operations to the selected physical console.
- Provides synchronous kernel console functions: `cngetc`, `cncheckc`, `cnpoll`, `cnputc`, `cndbctl`.

## Important Behavior
`cnopen` refuses access when `SYSCAP_RESTRICTEDROOT` is denied, forwards opens through saved physical ops to avoid recursion, and tracks logical vs physical opens so the physical device is not closed while either view remains open.

`cnwrite` sends output to `constty` when a tty has claimed virtual console output via `TIOCCONS`; otherwise it writes to the physical console and logs console output through `log_console`.

## Risks
The file explicitly relies on device-op interception, which is fragile around recursive opens and close ordering. Muting/unmuting can fail and must roll back `cn_mute`. Early boot initialization temporarily holds tty and VGA tokens while console drivers may print.
