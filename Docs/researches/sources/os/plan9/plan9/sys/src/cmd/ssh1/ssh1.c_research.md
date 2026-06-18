# File Research: sources/os/plan9/plan9/sys/src/cmd/ssh1/ssh1.c

Interactive SSH1 client command.

Key responsibilities:
- Parses cipher/auth/user/pty/interactive/raw/agent-forwarding options.
- Dials remote SSH port.
- Performs SSH1 client handshake and authentication.
- Optionally requests agent forwarding and pty.
- Runs remote command or shell.
- Copies stdin to SSH and SSH stdout/stderr back to local fds.
- Supports console raw mode, escape menu, window-size updates, and local shell escape.

Important functions:
- `main`: connection setup and command dispatch.
- `fromnet`: handles server output, exit status, disconnects, and agent channel messages.
- `fromstdin`: forked input loop sending stdin data/EOF.
- `menu`: handles escape commands.
- `system`: runs local command connected to remote stdin.
- `winchanges`: sends window-size updates.

Risks/quirks:
- Escape menu triggers on control-`\` byte.
- Agent forwarding assumes agent channels are the only channel traffic.
- Uses `/bin/rc` for local shell escape.
