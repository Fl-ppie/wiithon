from io import BytesIO
from typing import BinaryIO

from wiithon.structs.IMET import IMET
from wiithon.file_helper.u8 import U8


class BNR:
    def __init__(self) -> None:
        self.imet: IMET = IMET()
        self.u8: U8 = U8()

    @classmethod
    def read(cls, stream: BinaryIO) -> "BNR":
        obj = cls()
        obj.imet = IMET.read(stream)
        obj.u8  = U8.read(stream)
        return obj

    def write(self, stream: BinaryIO) -> None:
        self.imet.write(stream)
        self.u8.write(stream)

    def get_bytes(self) -> bytes:
        buf = BytesIO()
        self.write(buf)
        return buf.getvalue()

    # Titles (via IMET)
    @property
    def title(self) -> str:
        return self.imet.get_title(1)

    # Sub-files (U8 archive)
    def get_icon(self) -> bytes:
        return self.u8.get_file("meta/icon.bin")

    def get_banner(self) -> bytes:
        return self.u8.get_file("meta/banner.bin")

    def get_sound(self) -> bytes:
        return self.u8.get_file("meta/sound.bin")

    def replace_icon(self, data: bytes) -> None:
        self.u8.replace_file("meta/icon.bin", data)

    def replace_banner(self, data: bytes) -> None:
        self.u8.replace_file("meta/banner.bin", data)

    def replace_sound(self, data: bytes) -> None:
        self.u8.replace_file("meta/sound.bin", data)

    def __repr__(self) -> str:
        return f"BNR title={self.title!r}\n{self.imet}"
