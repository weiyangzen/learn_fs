# File Research: sources/os/linux/linux-stable/fs/afs/protocol_afs.h

## Scope

Defines small AFS3 fileserver protocol constants related to capability replies.

## API Surface

The header declares `AFSCAPABILITIESMAX` and capability word-0 flags for UAE error translation, 64-bit file operations, ACL write-lock behavior, and deprecated sane-ACL handling.

## Dependencies And Risks

These constants are consumed by RPC/probe code that interprets fileserver capabilities. Correct bit values matter because they drive feature downgrade/upgrade decisions in the client.
