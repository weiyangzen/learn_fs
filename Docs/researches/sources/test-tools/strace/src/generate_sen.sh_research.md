# sources/test-tools/strace/src/generate_sen.sh

Small shell generator for syscall entry-name (`SEN`) related generated data. It transforms syscall decoder names into generated definitions consumed by sysent tables. State is generated text only. Dependencies are POSIX shell, expected input ordering, and sysent shorthand conventions. Risks are name parsing drift and generated data falling out of sync with decoder functions. Tests should run regeneration, compile sysent tables, and verify new syscall decoders are represented.
