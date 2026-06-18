# File Research: sources/os/bsd/dragonflybsd/sys/sys/chio.h

SCSI media changer ioctl ABI for picker, slot, portal, and drive robotics.

Key responsibilities:
- Defines changer element types for medium transport, storage slots, import/export portals, and data-transfer drives.
- Defines structures for MOVE MEDIUM, EXCHANGE MEDIUM, POSITION TO ELEMENT, device parameters, volume tags, element status, status requests, and volume-tag mutation.
- Defines element status flags for full/access/exception/import-export/source/SCSI identity validity.
- Defines ioctls for move, exchange, position, get/set picker, get parameters, initialize elements, get status, and set volume tag.

Dependencies:
- Includes `sys/types.h` and `sys/ioccom.h`.

Notable risks:
- Comments warn element type numeric values are relied on by changer driver code as array offsets.
- Status request structures contain user pointers; driver copyin/copyout validation is critical.
