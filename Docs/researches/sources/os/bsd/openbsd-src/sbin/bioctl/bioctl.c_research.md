# File Research: sources/os/bsd/openbsd-src/sbin/bioctl/bioctl.c

OpenBSD bio/softraid control utility.

It parses command-line operations for inquiry, disk inquiry, alarm control, enclosure blink/unblink, hotspare/offline/rebuild state changes, patrol control, RAID/crypto volume creation, volume deletion, and crypto passphrase changes. It first tries to open the named device directly; if that fails, it opens `/dev/bio`, locates the named controller/device with `BIOCLOCATE`, and stores the returned bio cookie for later ioctls.

Inquiry walks controller volumes and disks using `BIOCINQ`, `BIOCVOL`, and `BIOCDISK`, formats volume/disk status, RAID level, size, cache mode, enclosure name, vendor, serial, and patrol progress. State-changing operations validate controller target locators or device nodes, resolve volume IDs, and issue `BIOCSETSTATE`, `BIOCBLINK`, `BIOCALARM`, `BIOCPATROL`, `BIOCCREATERAID`, `BIOCDELETERAID`, or `BIOCDISCIPLINE`.

Crypto support derives or generates KDF data for softraid crypto volumes. It supports passphrase files only when root-owned and mode `0600`, derives keys with PKCS#5 PBKDF2 or bcrypt PBKDF, auto-tunes bcrypt rounds to roughly one second, verifies interactive new passphrases, and zeroes KDF/passphrase material after use. Device-list parsing opens each chunk as a block device, stores `dev_t` values, enforces maximum list size, and rejects duplicates.

Notable constraints: many operations require `/dev/bio` or direct device ioctl support; creation enforces minimum disk counts by RAID level and permits crypto key-disk mode or passphrase KDF mode.
