#!/usr/bin/env python3
"""
EXIFMet - @rasplata_km

"""

import os
import sys
import json
import datetime
import struct
from pathlib import Path
import hashlib
import shutil

def clear_screen():
    """Очищает экран"""
    os.system('cls' if os.name == 'nt' else 'clear')

def center_text(text, width=74):
    """Центрирует текст"""
    return text.center(width)

def print_banner():
    """Баннер по центру"""
    clear_screen()
    banner = f"""
{'╔' + '═'*76 + '╗'}
{'║' + ' ' * 76 + '║'}
{'║' + center_text('███████╗██╗  ██╗██╗███████╗███╗   ███╗███████╗████████╗') + '║'}
{'║' + center_text('██╔════╝╚██╗██╔╝██║██╔════╝████╗ ████║██╔════╝╚══██╔══╝') + '║'}
{'║' + center_text('█████╗   ╚███╔╝ ██║█████╗  ██╔████╔██║█████╗     ██║   ') + '║'}
{'║' + center_text('██╔══╝   ██╔██╗ ██║██╔══╝  ██║╚██╔╝██║██╔══╝     ██║   ') + '║'}
{'║' + center_text('███████╗██╔╝ ██╗██║██║     ██║ ╚═╝ ██║███████╗   ██║   ') + '║'}
{'║' + center_text('╚══════╝╚═╝  ╚═╝╚═╝╚═╝     ╚═╝     ╚═╝╚══════╝   ╚═╝   ') + '║'}
{'║' + ' ' * 76 + '║'}
{'║' + center_text('by @rasplata_km') + '║'}
{'║' + ' ' * 76 + '║'}
{'╚' + '═'*76 + '╝'}

{'╔' + '═'*76 + '╗'}
{'║' + center_text('ИСПОЛЬЗОВАНИЕ: EXIFMet <файл> [--json] [--clean] [--info]') + '║'}
{'║' + center_text('ПРИМЕР: EXIFMet photo.jpg --json') + '║'}
{'║' + center_text('ФОРМАТЫ: JPEG PNG TIFF RAW PDF MP4') + '║'}
{'║' + center_text('ВЫТЯГИВАЕТ: EXIF GPS IPTC Хеши') + '║'}
{'║' + center_text('КОМАНДЫ: --help --version --json --batch --info --clean') + '║'}
{'╚' + '═'*76 + '╝'}
"""
    print(banner)

def show_menu():
    """Показывает меню выбора"""
    print("\n" + "="*50)
    print(" ВЫБЕРИТЕ ДЕЙСТВИЕ:")
    print("="*50)
    print(" 1 - Анализ файла")
    print(" 2 - Инфо о файле (--info)")
    print(" 3 - Извлечь метаданные в JSON (--extract)")
    print(" 4 - Очистить метаданные (--clean)")
    print(" 5 - Пакетная обработка (--batch)")
    print(" 6 - Справка (--help)")
    print(" 7 - Версия (--version)")
    print(" 0 - Выход")
    print("="*50)
    
    choice = input(" Ваш выбор: ").strip()
    return choice

def get_file_path():
    """Запрашивает путь к файлу"""
    print("\n" + "="*50)
    filepath = input(" Введите путь к файлу: ").strip()
    
    # Убираем кавычки если есть
    filepath = filepath.strip('"').strip("'")
    
    # Проверяем существование
    if not os.path.exists(filepath):
        print(f" ОШИБКА: Файл не найден: {filepath}")
        return None
    
    return filepath

class EXIFParser:
    """Собственный парсер EXIF без зависимостей"""
    
    EXIF_TAGS = {
        0x0100: 'ImageWidth', 0x0101: 'ImageLength', 0x0102: 'BitsPerSample',
        0x0103: 'Compression', 0x0106: 'PhotometricInterpretation', 0x010e: 'ImageDescription',
        0x010f: 'Make', 0x0110: 'Model', 0x0111: 'StripOffsets', 0x0112: 'Orientation',
        0x0115: 'SamplesPerPixel', 0x0117: 'StripByteCounts', 0x011a: 'XResolution',
        0x011b: 'YResolution', 0x011c: 'PlanarConfiguration', 0x0128: 'ResolutionUnit',
        0x0131: 'Software', 0x0132: 'DateTime', 0x013b: 'Artist', 0x013e: 'WhitePoint',
        0x013f: 'PrimaryChromaticities', 0x0211: 'YCbCrCoefficients', 0x0213: 'YCbCrPositioning',
        0x0214: 'ReferenceBlackWhite', 0x8298: 'Copyright', 0x8769: 'ExifOffset',
        0x8825: 'GPSInfo', 0x829a: 'ExposureTime', 0x829d: 'FNumber', 0x8822: 'ExposureProgram',
        0x8824: 'SpectralSensitivity', 0x8827: 'ISOSpeedRatings', 0x8828: 'OECF',
        0x8830: 'SensitivityType', 0x8831: 'StandardOutputSensitivity',
        0x8832: 'RecommendedExposureIndex', 0x8833: 'ISOSpeed', 0x9000: 'ExifVersion',
        0x9003: 'DateTimeOriginal', 0x9004: 'DateTimeDigitized', 0x9010: 'OffsetTime',
        0x9011: 'OffsetTimeOriginal', 0x9012: 'OffsetTimeDigitized', 0x9101: 'ComponentsConfiguration',
        0x9102: 'CompressedBitsPerPixel', 0x9201: 'ShutterSpeedValue', 0x9202: 'ApertureValue',
        0x9203: 'BrightnessValue', 0x9204: 'ExposureBiasValue', 0x9205: 'MaxApertureValue',
        0x9206: 'SubjectDistance', 0x9207: 'MeteringMode', 0x9208: 'LightSource',
        0x9209: 'Flash', 0x920a: 'FocalLength', 0x920b: 'FlashEnergy', 0x920c: 'SpatialFrequencyResponse',
        0x920d: 'Noise', 0x9211: 'ImageNumber', 0x9212: 'SecurityClassification',
        0x9213: 'ImageHistory', 0x9214: 'SubjectLocation', 0x9215: 'ExposureIndex',
        0x9216: 'TIFF/EPStandardID', 0x927c: 'MakerNote', 0x9286: 'UserComment',
        0x9290: 'SubsecTime', 0x9291: 'SubsecTimeOriginal', 0x9292: 'SubsecTimeDigitized',
        0x9400: 'Temperature', 0x9401: 'Humidity', 0x9402: 'Pressure', 0x9403: 'WaterDepth',
        0x9404: 'Acceleration', 0x9405: 'CameraElevationAngle', 0xa000: 'FlashpixVersion',
        0xa001: 'ColorSpace', 0xa002: 'PixelXDimension', 0xa003: 'PixelYDimension',
        0xa004: 'RelatedSoundFile', 0xa005: 'InteroperabilityOffset', 0xa20b: 'FlashEnergy',
        0xa20c: 'SpatialFrequencyResponse', 0xa20e: 'FocalPlaneXResolution',
        0xa20f: 'FocalPlaneYResolution', 0xa210: 'FocalPlaneResolutionUnit',
        0xa214: 'SubjectLocation', 0xa215: 'ExposureIndex', 0xa217: 'SensingMethod',
        0xa300: 'FileSource', 0xa301: 'SceneType', 0xa302: 'CFAPattern',
        0xa401: 'CustomRendered', 0xa402: 'ExposureMode', 0xa403: 'WhiteBalance',
        0xa404: 'DigitalZoomRatio', 0xa405: 'FocalLengthIn35mmFilm',
        0xa406: 'SceneCaptureType', 0xa407: 'GainControl', 0xa408: 'Contrast',
        0xa409: 'Saturation', 0xa40a: 'Sharpness', 0xa40b: 'DeviceSettingDescription',
        0xa40c: 'SubjectDistanceRange', 0xa420: 'ImageUniqueID', 0xa430: 'CameraOwnerName',
        0xa431: 'BodySerialNumber', 0xa432: 'LensSpecification', 0xa433: 'LensMake',
        0xa434: 'LensModel', 0xa435: 'LensSerialNumber', 0xa480: 'GDALMetadata',
        0xa481: 'GDALNoData', 0xa500: 'Gamma',
    }
    
    GPS_TAGS = {
        0x0000: 'GPSVersionID', 0x0001: 'GPSLatitudeRef', 0x0002: 'GPSLatitude',
        0x0003: 'GPSLongitudeRef', 0x0004: 'GPSLongitude', 0x0005: 'GPSAltitudeRef',
        0x0006: 'GPSAltitude', 0x0007: 'GPSTimeStamp', 0x0008: 'GPSSatellites',
        0x0009: 'GPSStatus', 0x000a: 'GPSMeasureMode', 0x000b: 'GPSDOP',
        0x000c: 'GPSSpeedRef', 0x000d: 'GPSSpeed', 0x000e: 'GPSTrackRef',
        0x000f: 'GPSTrack', 0x0010: 'GPSImgDirectionRef', 0x0011: 'GPSImgDirection',
        0x0012: 'GPSMapDatum', 0x0013: 'GPSDestLatitudeRef', 0x0014: 'GPSDestLatitude',
        0x0015: 'GPSDestLongitudeRef', 0x0016: 'GPSDestLongitude', 0x0017: 'GPSDestBearingRef',
        0x0018: 'GPSDestBearing', 0x0019: 'GPSDestDistanceRef', 0x001a: 'GPSDestDistance',
        0x001b: 'GPSProcessingMethod', 0x001c: 'GPSAreaInformation', 0x001d: 'GPSDateStamp',
        0x001e: 'GPSDifferential', 0x001f: 'GPSHPositioningError',
    }
    
    def __init__(self, filepath):
        self.filepath = filepath
        self.exif_data = {}
        self.gps_data = {}
        
    def parse(self):
        """Парсинг EXIF данных"""
        try:
            with open(self.filepath, 'rb') as f:
                data = f.read()
            
            if data[:2] == b'\xff\xd8':
                return self._parse_jpeg(data)
            elif data[:8] == b'\x89\x50\x4e\x47\x0d\x0a\x1a\x0a':
                return self._parse_png(data)
            elif data[:2] == b'II' or data[:2] == b'MM':
                return self._parse_tiff(data)
            else:
                return self._parse_raw_exif(data)
                
        except Exception as e:
            return {'error': str(e)}
    
    def _parse_jpeg(self, data):
        """Парсинг JPEG EXIF"""
        pos = 2
        while pos < len(data) - 10:
            if data[pos:pos+2] == b'\xff\xe1':
                length = struct.unpack('>H', data[pos+2:pos+4])[0]
                if data[pos+4:pos+10] == b'Exif\x00\x00':
                    exif_bytes = data[pos+10:pos+4+length]
                    return self._parse_exif_block(exif_bytes)
                pos += length + 2
            elif data[pos:pos+2] == b'\xff\xe0':
                length = struct.unpack('>H', data[pos+2:pos+4])[0]
                pos += length + 2
            elif data[pos:pos+2] == b'\xff\xd8' or data[pos:pos+2] == b'\xff\xd9':
                pos += 2
            else:
                pos += 1
                while pos < len(data) and data[pos] != 0xff:
                    pos += 1
        return {}
    
    def _parse_exif_block(self, data):
        """Парсинг EXIF блока"""
        exif = {}
        
        if data[:2] == b'II':
            endian = '<'
        elif data[:2] == b'MM':
            endian = '>'
        else:
            return exif
        
        if data[2:4] != b'\x2a\x00' and data[2:4] != b'\x00\x2a':
            return exif
        
        offset = struct.unpack(endian + 'I', data[4:8])[0]
        self._parse_ifd(data, offset, endian, exif)
        
        if 'ExifOffset' in exif:
            self._parse_ifd(data, exif['ExifOffset'], endian, exif)
        
        if 'GPSInfo' in exif:
            self._parse_gps(data, exif['GPSInfo'], endian)
        
        return exif
    
    def _parse_ifd(self, data, offset, endian, exif):
        """Парсинг IFD"""
        try:
            count = struct.unpack(endian + 'H', data[offset:offset+2])[0]
            pos = offset + 2
            
            for _ in range(count):
                if pos + 12 > len(data):
                    break
                    
                tag = struct.unpack(endian + 'H', data[pos:pos+2])[0]
                typ = struct.unpack(endian + 'H', data[pos+2:pos+4])[0]
                length = struct.unpack(endian + 'I', data[pos+4:pos+8])[0]
                value_offset = struct.unpack(endian + 'I', data[pos+8:pos+12])[0]
                
                tag_name = self.EXIF_TAGS.get(tag, f'0x{tag:04x}')
                
                if typ == 1:  # BYTE
                    if length > 4:
                        val = data[value_offset:value_offset+length]
                    else:
                        val = data[pos+8:pos+8+length]
                    exif[tag_name] = val.hex() if len(val) > 20 else val
                    
                elif typ == 2:  # ASCII
                    if length > 4:
                        val = data[value_offset:value_offset+length-1]
                    else:
                        val = data[pos+8:pos+8+length-1]
                    try:
                        exif[tag_name] = val.decode('utf-8', errors='ignore')
                    except:
                        exif[tag_name] = str(val)
                        
                elif typ == 3:  # SHORT
                    if length > 2:
                        vals = []
                        for i in range(length):
                            v = struct.unpack(endian + 'H', data[value_offset+i*2:value_offset+i*2+2])[0]
                            vals.append(v)
                        exif[tag_name] = vals if len(vals) > 1 else vals[0]
                    else:
                        exif[tag_name] = struct.unpack(endian + 'H', data[pos+8:pos+10])[0]
                        
                elif typ == 4:  # LONG
                    if length > 1:
                        vals = []
                        for i in range(length):
                            v = struct.unpack(endian + 'I', data[value_offset+i*4:value_offset+i*4+4])[0]
                            vals.append(v)
                        exif[tag_name] = vals if len(vals) > 1 else vals[0]
                    else:
                        exif[tag_name] = struct.unpack(endian + 'I', data[pos+8:pos+12])[0]
                        
                elif typ == 5:  # RATIONAL
                    if length > 1:
                        vals = []
                        for i in range(length):
                            num = struct.unpack(endian + 'I', data[value_offset+i*8:value_offset+i*8+4])[0]
                            den = struct.unpack(endian + 'I', data[value_offset+i*8+4:value_offset+i*8+8])[0]
                            vals.append(num/den if den != 0 else 0)
                        exif[tag_name] = vals if len(vals) > 1 else vals[0]
                    else:
                        num = struct.unpack(endian + 'I', data[value_offset:value_offset+4])[0]
                        den = struct.unpack(endian + 'I', data[value_offset+4:value_offset+8])[0]
                        exif[tag_name] = num/den if den != 0 else 0
                        
                elif typ == 7:  # UNDEFINED
                    if length > 4:
                        val = data[value_offset:value_offset+length]
                    else:
                        val = data[pos+8:pos+8+length]
                    exif[tag_name] = val.hex() if len(val) > 20 else val
                    
                elif typ == 9:  # SLONG
                    if length > 1:
                        vals = []
                        for i in range(length):
                            v = struct.unpack(endian + 'i', data[value_offset+i*4:value_offset+i*4+4])[0]
                            vals.append(v)
                        exif[tag_name] = vals if len(vals) > 1 else vals[0]
                    else:
                        exif[tag_name] = struct.unpack(endian + 'i', data[pos+8:pos+12])[0]
                        
                elif typ == 10:  # SRATIONAL
                    if length > 1:
                        vals = []
                        for i in range(length):
                            num = struct.unpack(endian + 'i', data[value_offset+i*8:value_offset+i*8+4])[0]
                            den = struct.unpack(endian + 'i', data[value_offset+i*8+4:value_offset+i*8+8])[0]
                            vals.append(num/den if den != 0 else 0)
                        exif[tag_name] = vals if len(vals) > 1 else vals[0]
                    else:
                        num = struct.unpack(endian + 'i', data[value_offset:value_offset+4])[0]
                        den = struct.unpack(endian + 'i', data[value_offset+4:value_offset+8])[0]
                        exif[tag_name] = num/den if den != 0 else 0
                
                pos += 12
            
            next_ifd = struct.unpack(endian + 'I', data[offset+2+count*12:offset+4+count*12])[0]
            if next_ifd:
                self._parse_ifd(data, next_ifd, endian, exif)
                
        except Exception as e:
            pass
    
    def _parse_gps(self, data, offset, endian):
        """Парсинг GPS данных"""
        try:
            count = struct.unpack(endian + 'H', data[offset:offset+2])[0]
            pos = offset + 2
            
            for _ in range(count):
                tag = struct.unpack(endian + 'H', data[pos:pos+2])[0]
                typ = struct.unpack(endian + 'H', data[pos+2:pos+4])[0]
                length = struct.unpack(endian + 'I', data[pos+4:pos+8])[0]
                value_offset = struct.unpack(endian + 'I', data[pos+8:pos+12])[0]
                
                tag_name = self.GPS_TAGS.get(tag, f'0x{tag:04x}')
                
                if typ == 5:  # RATIONAL
                    if length > 1:
                        vals = []
                        for i in range(length):
                            num = struct.unpack(endian + 'I', data[value_offset+i*8:value_offset+i*8+4])[0]
                            den = struct.unpack(endian + 'I', data[value_offset+i*8+4:value_offset+i*8+8])[0]
                            vals.append(num/den if den != 0 else 0)
                        self.gps_data[tag_name] = vals if len(vals) > 1 else vals[0]
                    else:
                        num = struct.unpack(endian + 'I', data[value_offset:value_offset+4])[0]
                        den = struct.unpack(endian + 'I', data[value_offset+4:value_offset+8])[0]
                        self.gps_data[tag_name] = num/den if den != 0 else 0
                elif typ == 2:  # ASCII
                    val = data[value_offset:value_offset+length-1]
                    self.gps_data[tag_name] = val.decode('utf-8', errors='ignore')
                else:
                    self.gps_data[tag_name] = struct.unpack(endian + 'I', data[value_offset:value_offset+4])[0]
                
                pos += 12
                
        except Exception as e:
            pass
    
    def _parse_png(self, data):
        """Парсинг PNG метаданных"""
        png_data = {}
        pos = 8
        
        while pos < len(data) - 8:
            length = struct.unpack('>I', data[pos:pos+4])[0]
            chunk_type = data[pos+4:pos+8].decode('ascii', errors='ignore')
            
            if chunk_type == 'tEXt':
                text = data[pos+8:pos+8+length]
                try:
                    text = text.decode('latin-1')
                    if '=' in text:
                        key, val = text.split('=', 1)
                        png_data[key] = val
                except:
                    pass
            elif chunk_type == 'iTXt':
                text = data[pos+8:pos+8+length]
                try:
                    text = text.decode('utf-8', errors='ignore')
                    parts = text.split('\x00')
                    if len(parts) >= 4:
                        png_data[parts[2]] = parts[3]
                except:
                    pass
            
            pos += length + 12
        
        return png_data
    
    def _parse_tiff(self, data):
        """Парсинг TIFF файлов"""
        return self._parse_exif_block(data)
    
    def _parse_raw_exif(self, data):
        """Парсинг EXIF из RAW файлов"""
        for i in range(0, len(data) - 10, 2):
            if data[i:i+6] == b'Exif\x00\x00':
                return self._parse_exif_block(data[i+6:])
        return {}

class EXIFMetaExtractor:
    def __init__(self, filepath):
        self.filepath = Path(filepath)
        self.metadata = {
            "file_info": {},
            "exif": {},
            "gps": {},
            "exif_raw": {},
            "checksums": {}
        }
        
    def extract_all(self):
        """Главный метод для вытягивания всего"""
        print("\n" + "="*50)
        print(" Анализ:", self.filepath.name)
        print("="*50 + "\n")
        
        self._get_file_info()
        self._extract_exif()
        self._extract_gps()
        self._calculate_checksums()
        
        return self.metadata
    
    def _get_file_info(self):
        """Базовая информация о файле"""
        stat = os.stat(self.filepath)
        self.metadata["file_info"] = {
            "имя_файла": self.filepath.name,
            "размер_байт": stat.st_size,
            "размер_МБ": round(stat.st_size / (1024*1024), 2),
            "путь": str(self.filepath.absolute()),
            "расширение": self.filepath.suffix.lower(),
            "создан": datetime.datetime.fromtimestamp(stat.st_ctime).isoformat(),
            "изменен": datetime.datetime.fromtimestamp(stat.st_mtime).isoformat(),
            "доступ": datetime.datetime.fromtimestamp(stat.st_atime).isoformat()
        }
        print("Файл:", self.metadata['file_info']['имя_файла'])
        print("Размер:", self.metadata['file_info']['размер_МБ'], "MB")
        print("Путь:", self.metadata['file_info']['путь'])
    
    def _extract_exif(self):
        """Вытягиваем EXIF данные"""
        print("\nEXIF данные:")
        
        try:
            parser = EXIFParser(self.filepath)
            exif_data = parser.parse()
            
            if exif_data and not exif_data.get('error'):
                self.metadata["exif"] = exif_data
                
                important_tags = [
                    'Make', 'Model', 'DateTimeOriginal', 'DateTimeDigitized',
                    'ExposureTime', 'FNumber', 'ISOSpeedRatings', 'FocalLength',
                    'MeteringMode', 'Flash', 'WhiteBalance', 'ExposureProgram',
                    'LensModel', 'LensMake', 'Software', 'Artist', 'Copyright'
                ]
                
                for tag in important_tags:
                    if tag in exif_data:
                        print(f"   {tag}: {exif_data[tag]}")
                
                other_tags = {k: v for k, v in exif_data.items() if k not in important_tags}
                if other_tags:
                    print(f"\n   Дополнительные теги ({len(other_tags)} шт.):")
                    for i, (k, v) in enumerate(list(other_tags.items())[:10]):
                        if isinstance(v, (int, float, str)):
                            print(f"   {k}: {v}")
                    if len(other_tags) > 10:
                        print(f"   ... и еще {len(other_tags)-10} тегов")
                
                self.metadata["exif_raw"] = exif_data
                
            else:
                print("   EXIF данные не найдены")
                
        except Exception as e:
            print(f"   Ошибка: {e}")
            self.metadata["exif"]["error"] = str(e)
    
    def _extract_gps(self):
        """Вытягиваем GPS координаты"""
        try:
            parser = EXIFParser(self.filepath)
            parser.parse()
            
            if parser.gps_data:
                print("\nGPS координаты:")
                self.metadata["gps"] = parser.gps_data
                
                for key, val in parser.gps_data.items():
                    print(f"   {key}: {val}")
                
                if 'GPSLatitude' in parser.gps_data and 'GPSLongitude' in parser.gps_data:
                    lat = self._convert_to_degrees(parser.gps_data['GPSLatitude'])
                    lon = self._convert_to_degrees(parser.gps_data['GPSLongitude'])
                    
                    if parser.gps_data.get('GPSLatitudeRef') == 'S':
                        lat = -lat
                    if parser.gps_data.get('GPSLongitudeRef') == 'W':
                        lon = -lon
                    
                    self.metadata["gps"]["decimal"] = {
                        "latitude": lat,
                        "longitude": lon
                    }
                    print(f"\n   Координаты:")
                    print(f"   Широта: {lat:.6f}")
                    print(f"   Долгота: {lon:.6f}")
                    print(f"   Карта: https://maps.google.com/maps?q={lat},{lon}")
                    
        except Exception as e:
            print(f"   Ошибка GPS: {e}")
    
    def _convert_to_degrees(self, value):
        """Конвертирует GPS координаты в градусы"""
        if isinstance(value, list) and len(value) >= 3:
            return float(value[0]) + (float(value[1]) / 60.0) + (float(value[2]) / 3600.0)
        return value
    
    def _calculate_checksums(self):
        """Вычисляем хеш-суммы"""
        print("\nХеши:")
        try:
            with open(self.filepath, 'rb') as f:
                data = f.read()
                
                checksums = {
                    'MD5': hashlib.md5(data).hexdigest(),
                    'SHA1': hashlib.sha1(data).hexdigest(),
                    'SHA256': hashlib.sha256(data).hexdigest()
                }
                
                self.metadata["checksums"] = checksums
                for algo, value in checksums.items():
                    print(f"   {algo}: {value[:16]}...")
                    
        except Exception as e:
            print(f"   Ошибка: {e}")
    
    def save_report(self):
        """Сохраняет отчет на рабочий стол"""
        desktop = Path.home() / 'Desktop'
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'EXIF_{timestamp}.txt'
        filepath = desktop / filename
        
        print(f"\nСохранение: {filepath}")
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write("="*60 + "\n")
            f.write("EXIF META DATA REPORT\n")
            f.write(f"Время: {datetime.datetime.now().isoformat()}\n")
            f.write(f"Файл: {self.filepath.name}\n")
            f.write("="*60 + "\n\n")
            
            for section, data in self.metadata.items():
                if data:
                    f.write(f"\n{section.upper()}:\n")
                    f.write("-"*40 + "\n")
                    
                    if isinstance(data, dict):
                        for key, value in data.items():
                            if isinstance(value, dict):
                                f.write(f"\n{key}:\n")
                                for k, v in value.items():
                                    f.write(f"  {k}: {v}\n")
                            else:
                                f.write(f"{key}: {value}\n")
                    elif isinstance(data, list):
                        for i, item in enumerate(data, 1):
                            f.write(f"{i}. {item}\n")
                    else:
                        f.write(f"{data}\n")
            
            f.write("\n" + "="*60 + "\n")
            f.write("Отчет создан @rasplata_km\n")
        
        return filepath

def main():
    # Обработка аргументов командной строки
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
        file_path = file_path.strip('"').strip("'")
        
        # Если файл не существует, может это команда?
        if file_path in ['--help', '-h']:
            print_banner()
            return
        elif file_path in ['--version', '-v']:
            clear_screen()
            print("="*50)
            print(" EXIFMet 1.0")
            print(" by @rasplata_km")
            print("="*50)
            return
        
        if not os.path.exists(file_path):
            print(f"ОШИБКА: Файл не найден: {file_path}")
            return

        # Проверяем дополнительные флаги
        json_export = '--json' in sys.argv or '-j' in sys.argv
        clean_export = '--clean' in sys.argv or '-c' in sys.argv
        info_only = '--info' in sys.argv or '-i' in sys.argv
        
        try:
            extractor = EXIFMetaExtractor(file_path)
            
            if info_only:
                extractor._get_file_info()
                extractor._calculate_checksums()
                return
            
            if clean_export:
                print("\nОчистка метаданных из файла...")
                # Создаем копию без метаданных
                out_path = Path(file_path).stem + "_CLEANED" + Path(file_path).suffix
                shutil.copy2(file_path, out_path)
                
                # Простая очистка: перезапись базовых маркеров EXIF в копии (для JPEG)
                if Path(file_path).suffix.lower() in ['.jpg', '.jpeg']:
                    with open(out_path, 'r+b') as f:
                        content = f.read()
                        # Ищем и заменяем маркер EXIF на пустоту
                        new_content = content.replace(b'\xff\xe1', b'\xff\xe0', 1) 
                        f.seek(0)
                        f.write(new_content)
                        f.truncate()
                    print(f"Очищенный файл сохранен: {out_path}")
                elif Path(file_path).suffix.lower() in ['.png']:
                    print(f"Примечание: Для PNG файлов метаданные удалены не будут, сохранена копия: {out_path}")
                else:
                    print(f"Примечание: Автоматическая очистка поддерживается только для JPEG. Сохранена копия: {out_path}")
                return

            metadata = extractor.extract_all()
            
            if json_export:
                desktop = Path.home() / 'Desktop'
                timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
                json_file = desktop / f'EXIF_{timestamp}.json'
                with open(json_file, 'w', encoding='utf-8') as f:
                    json.dump(metadata, f, indent=2, ensure_ascii=False, default=str)
                print(f"\nJSON сохранен: {json_file}")
            else:
                report_file = extractor.save_report()
                print("\n" + "="*50)
                print("Готово!")
                print(f"Отчет: {report_file}")
                print("="*50)
                
        except Exception as e:
            print(f"Ошибка: {e}")
        return

    # Интерактивный режим (Меню)
    while True:
        print_banner()
        choice = show_menu()
        
        if choice == '0':
            clear_screen()
            print("\n Выход...")
            break
            
        elif choice == '1':
            filepath = get_file_path()
            if filepath:
                try:
                    extractor = EXIFMetaExtractor(filepath)
                    metadata = extractor.extract_all()
                    report_file = extractor.save_report()
                    
                    print("\n" + "="*50)
                    print("Готово!")
                    print(f"Отчет: {report_file}")
                    print("="*50)
                    print(f"\nEXIF: {len(metadata['exif'])} полей")
                    print(f"GPS: {'Да' if metadata['gps'] else 'Нет'}")
                    print()
                    
                except Exception as e:
                    print(f"Ошибка: {e}")
            
            input("\n Нажмите Enter для продолжения...")
            
        elif choice == '2':  # --info
            filepath = get_file_path()
            if filepath:
                try:
                    extractor = EXIFMetaExtractor(filepath)
                    extractor._get_file_info()
                    extractor._calculate_checksums()
                except Exception as e:
                    print(f"Ошибка: {e}")
            input("\n Нажмите Enter для продолжения...")
            
        elif choice == '3':  # --extract (сохранить в JSON)
            filepath = get_file_path()
            if filepath:
                try:
                    extractor = EXIFMetaExtractor(filepath)
                    metadata = extractor.extract_all()
                    
                    desktop = Path.home() / 'Desktop'
                    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
                    json_file = desktop / f'EXIF_{timestamp}.json'
                    
                    with open(json_file, 'w', encoding='utf-8') as f:
                        json.dump(metadata, f, indent=2, ensure_ascii=False, default=str)
                    
                    print(f"\nJSON сохранен: {json_file}")
                except Exception as e:
                    print(f"Ошибка: {e}")
            
            input("\n Нажмите Enter для продолжения...")
            
        elif choice == '4':  # --clean
            filepath = get_file_path()
            if filepath:
                try:
                    print("\nОчистка метаданных из файла...")
                    out_path = Path(filepath).stem + "_CLEANED" + Path(filepath).suffix
                    shutil.copy2(filepath, out_path)
                    
                    if Path(filepath).suffix.lower() in ['.jpg', '.jpeg']:
                        with open(out_path, 'r+b') as f:
                            content = f.read()
                            new_content = content.replace(b'\xff\xe1', b'\xff\xe0', 1)
                            f.seek(0)
                            f.write(new_content)
                            f.truncate()
                        print(f"Очищенный файл сохранен: {out_path}")
                    else:
                        print(f"Примечание: Автоматическая очистка поддерживается только для JPEG. Сохранена копия: {out_path}")
                except Exception as e:
                    print(f"Ошибка: {e}")
            input("\n Нажмите Enter для продолжения...")
            
        elif choice == '5':  # Batch
            print("\nПакетная обработка")
            folder = input(" Введите путь к папке: ").strip()
            folder = folder.strip('"').strip("'")
            
            if os.path.exists(folder) and os.path.isdir(folder):
                images = []
                for ext in ['.jpg', '.jpeg', '.png', '.tiff', '.tif', '.bmp', '.gif', '.cr2', '.nef', '.arw', '.dng']:
                    images.extend(Path(folder).glob(f'*{ext}'))
                    images.extend(Path(folder).glob(f'*{ext.upper()}'))
                
                if images:
                    print(f"\n Найдено файлов: {len(images)}")
                    for img in images[:10]:
                        print(f"  • {img.name}")
                    if len(images) > 10:
                        print(f"  ... и еще {len(images)-10}")
                    
                    process = input("\n Обработать все? (y/n): ").strip().lower()
                    if process == 'y':
                        desktop = Path.home() / 'Desktop'
                        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
                        batch_file = desktop / f'BATCH_REPORT_{timestamp}.txt'
                        
                        with open(batch_file, 'w', encoding='utf-8') as f:
                            f.write("="*60 + "\n")
                            f.write("BATCH EXIF REPORT\n")
                            f.write(f"Время: {datetime.datetime.now().isoformat()}\n")
                            f.write(f"Папка: {folder}\n")
                            f.write("="*60 + "\n\n")
                            
                            for img in images:
                                try:
                                    extractor = EXIFMetaExtractor(img)
                                    metadata = extractor.extract_all()
                                    f.write(f"\nФайл: {img.name}\n")
                                    f.write("-"*40 + "\n")
                                    f.write(f"Размер: {metadata['file_info']['размер_МБ']} MB\n")
                                    f.write(f"EXIF: {len(metadata['exif'])} полей\n")
                                    f.write(f"GPS: {'Да' if metadata['gps'] else 'Нет'}\n")
                                except Exception as e:
                                    f.write(f"Ошибка: {e}\n")
                        
                        print(f"\nОтчет сохранен: {batch_file}")
                else:
                    print(" Изображений не найдено")
            else:
                print(" Папка не найдена")
            
            input("\n Нажмите Enter для продолжения...")
            
        elif choice == '6':
            print_banner()
            input("\n Нажмите Enter для продолжения...")
            
        elif choice == '7':
            clear_screen()
            print("\n" + "="*50)
            print(" EXIFMet")
            print(" by @rasplata_km")
            print("="*50)
            input("\n Нажмите Enter для продолжения...")
            
        else:
            print(" Неверный выбор")
            input("\n Нажмите Enter для продолжения...")

if __name__ == "__main__":
    main()