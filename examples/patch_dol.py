import sys
sys.path.insert(0, "../src")

from file_helper.dol import DOL
from helpers import PowerPC as ppc
from helpers.Enums import WiiPartType
from WiiIsoReader import WiiIsoReader
from builder.WiiDiscBuilder import WiiDiscBuilder
from builder.CopyBuilder import CopyBuilder


# Patch addresses
PATCH_ADDR_NOP   = 0x80258a0c
PATCH_ADDR_LI    = 0x80258a10
PATCH_ADDR_BL_FROM   = 0x80258a14
PATCH_ADDR_BL_TARGET = 0x80f58a14


def apply_patches(dol: DOL) -> None:
    """All patches go here. Used for both the standalone DOL and the ISO DOL"""

    # Patch 1: write a nop at PATCH_ADDR_NOP
    dol.write_at(PATCH_ADDR_NOP, ppc.nop())
    print(f"  nop         @ {PATCH_ADDR_NOP:#010x}")

    # Patch 2: force li r3, 1 at PATCH_ADDR_LI
    dol.write_at(PATCH_ADDR_LI, ppc.li(3, 1))
    print(f"  li r3, 1    @ {PATCH_ADDR_LI:#010x}")

    # Patch 3: redirect a bl
    dol.write_at(PATCH_ADDR_BL_FROM, ppc.bl(PATCH_ADDR_BL_TARGET, PATCH_ADDR_BL_FROM))
    print(f"  bl {PATCH_ADDR_BL_TARGET:#010x} @ {PATCH_ADDR_BL_FROM:#010x}")


# A .dol file
def patch_standalone_dol(src: str, dst: str) -> None:
    print(f"\n--- Patching standalone DOL ---")
    print(f"  Source : {src}")
    print(f"  Output : {dst}")

    with open(src, "rb") as f:
        dol = DOL.read(f)

    apply_patches(dol)

    with open(dst, "wb") as f:
        f.write(dol.to_bytes())

    print("  Done.")


# Directly inside a Wii ISO
def patch_iso_dol(src_iso: str, dst_iso: str) -> None:
    print(f"\n--- Patching DOL inside ISO ---")
    print(f"  Source : {src_iso}")
    print(f"  Output : {dst_iso}")

    with WiiIsoReader(src_iso) as reader:
        print(f"  Game   : {reader.disc_header.game_title.strip()}")
        print(f"  ID     : {reader.disc_header.game_id.decode()}")

        builder = WiiDiscBuilder(reader.disc_header, reader.region)

        with open(dst_iso, "w+b") as dest:
            for entry in reader.partitions:
                copy_builder = CopyBuilder(
                    reader, entry,
                    dol_modifier=apply_patches if entry.part_type == WiiPartType.DATA else None,
                )
                builder.add_partition(dest, copy_builder, None)

            builder.finish(dest)
    print("  Done.")

# This file has been used to test if patching a real dol works (and it is !)
if __name__ == "__main__":
    patch_standalone_dol("../assets/main.dol", "../assets/main_patched.dol")
    patch_iso_dol("../assets/smg.iso", "../assets/smg_patched.iso")
