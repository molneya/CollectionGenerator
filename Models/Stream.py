
import struct

class StreamDecoder:
    @staticmethod
    def bool(bytestream) -> bool:
        return struct.unpack('<?', bytestream.read(0x01))[0]

    @staticmethod
    def byte(bytestream) -> int:
        return struct.unpack('<B', bytestream.read(0x01))[0]

    @staticmethod
    def short(bytestream) -> int:
        return struct.unpack('<H', bytestream.read(0x02))[0]

    @staticmethod
    def int(bytestream) -> int:
        return struct.unpack('<I', bytestream.read(0x04))[0]

    @staticmethod
    def long(bytestream) -> int:
        return struct.unpack('<L', bytestream.read(0x08))[0]

    @staticmethod
    def single(bytestream) -> float:
        return struct.unpack('<f', bytestream.read(0x04))[0]

    @staticmethod
    def uleb128(bytestream) -> int:
        a = bytearray()
        while True:
            b = ord(bytestream.read(0x01))
            a.append(b)
            if (b & 0x80) == 0:
                break
        r = 0
        for i, e in enumerate(a):
            r = r + ((e & 0x7f) << (i * 7))
        return r

    @staticmethod
    def string(bytestream) -> str:
        length = struct.unpack('<B', bytestream.read(0x01))[0]
        return struct.unpack(f'<{length}s', bytestream.read(length))[0].decode('utf-8')

    @staticmethod
    def sstring(bytestream) -> None:
        length = struct.unpack('<B', bytestream.read(0x01))[0]
        bytestream.seek(length, 1)

    @staticmethod
    def ulebstring(bytestream) -> str:
        if StreamDecoder.byte(bytestream) == 0x00:
            return ""
        length = StreamDecoder.uleb128(bytestream)
        return struct.unpack(f'<{length}s', bytestream.read(length))[0].decode('utf-8')

    @staticmethod
    def ulebsstring(bytestream) -> None:
        if StreamDecoder.byte(bytestream) == 0x00:
            return
        length = StreamDecoder.uleb128(bytestream)
        bytestream.seek(length, 1)

class StreamEncoder:
    @staticmethod
    def byte(value, buffer) -> None:
        r = struct.pack('<B', value)
        buffer.write(r)

    @staticmethod
    def int(value, buffer) -> None:
        r = struct.pack('<I', value)
        buffer.write(r)

    @staticmethod
    def uleb128(value, buffer) -> None:
        r = []
        while True:
            byte = value & 0x7f
            value = value >> 7
            if value == 0:
                r.append(byte)
                buffer.write(bytearray(r))
                return
            r.append(0x80 | byte)

    @staticmethod
    def string(value, buffer) -> None:
        encoded_value = value.encode('utf-8')
        r = struct.pack('<B', len(encoded_value))
        buffer.write(r)
        r = struct.pack(f'<{len(encoded_value)}s', encoded_value)
        buffer.write(r)

    @staticmethod
    def ulebstring(value, buffer) -> None:
        if value == "":
            StreamEncoder.byte(0x00, buffer)
        StreamEncoder.byte(0x0b, buffer)
        encoded_value = value.encode('utf-8')
        StreamEncoder.uleb128(len(encoded_value), buffer)
        r = struct.pack(f'<{len(encoded_value)}s', encoded_value)
        buffer.write(r)
