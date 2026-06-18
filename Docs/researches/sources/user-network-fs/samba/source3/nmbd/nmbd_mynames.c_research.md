# sources/user-network-fs/samba/source3/nmbd/nmbd_mynames.c

## Purpose
Initializes Samba's configured NetBIOS names and registers them, the workgroup names, and Samba magic names across broadcast and unicast subnets. It also releases WINS names and periodically refreshes WINS registrations.

## Important APIs, Types, And Functions
Public APIs are `nmbd_init_my_netbios_names()`, `my_netbios_names()`, `register_my_workgroup_one_subnet()`, `register_my_workgroup_and_names()`, `release_wins_names()`, and `refresh_my_names()`. Internal helpers include `add_unique_netbios_name()`, `my_name_register_failed()`, and `insert_refresh_name_into_unicast()`.

## Control Flow
Initialization builds a talloc array of primary name plus unique aliases. Per subnet registration creates the workgroup, adds magic names, registers each configured name as `<20>`, `<03>`, and `<00>`, then initiates workgroup startup. `register_my_workgroup_and_names()` runs that across subnets, adds unicast mirrors for names and workgroup `<00>/<1e>`, appends cluster addresses when configured, and adds remote-broadcast magic names. `release_wins_names()` releases active unicast `SELF_NAME` records. `refresh_my_names()` queues WINS refreshes for due unicast self names and pre-extends local refresh/death times to avoid duplicate queueing.

## State And Persistence
Owns static `mynames` and populates workgroup/namelist state. WINS-client unicast names use refresh TTLs; broadcast-only mirrors are permanent. Release and refresh effects persist through namelist/WINS storage layers.

## Dependencies, Risks, And Test Signals
Depends on workgroup creation, name registration/release, WINS refresh, cluster config, subnet globals, and namelist mutation. Risks include duplicate alias handling, partial registration failures, wrong unicast TTL mode, and repeated cluster IP appends. Test signals include alias uniqueness, expected `<20>/<03>/<00>` registrations, unicast mirrors per interface, refresh queueing once per due record, and release of WINS self names.
