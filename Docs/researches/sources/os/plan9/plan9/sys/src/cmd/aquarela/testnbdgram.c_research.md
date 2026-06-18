# File Research: sources/os/plan9/plan9/sys/src/cmd/aquarela/testnbdgram.c

NetBIOS datagram browsing test tool.

Key points:
- Listens for datagrams addressed to the primary domain browser name.
- `deliver` parses SMB transaction datagrams, filters for `\MAILSLOT\BROWSE`, and decodes host announcement fields.
- Prints server name, announcement period, version, type, browser version, and comment.
- Main loop periodically sends a host announcement.

Dependencies:
- Uses NetBIOS datagram APIs, SMB header parsing, transaction decoding, and browser announcement helpers.

Notable behavior:
- Deliberately avoids validating the high half of the browser signature because some devices send nonstandard values.
