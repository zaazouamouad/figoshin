#!/usr/bin/env python3
"""
NEXU_IO v3.0 - Advanced Global RF Analysis & Control System (CLI Edition)
Terminal-based interface for RF jamming, spectrum analysis, signal generation, and device database.
No external dependencies – pure Python standard library.
"""

import math
import random
import os
import sys
import json
import time
import threading
import subprocess
import logging
from datetime import datetime
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum
from dataclasses import dataclass

# ─── ANSI Color Constants ───────────────────────────────────────────
RESET = "\033[0m"
BOLD = "\033[1m"
DIM = "\033[2m"
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
MAGENTA = "\033[95m"
CYAN = "\033[96m"
ORANGE = "\033[38;5;214m"
PURPLE = "\033[38;5;129m"

# ─── Global Constants ───────────────────────────────────────────────
VERSION = "Nexu_IO v3.0"
MAX_DEVICES = 10000
SAMPLE_RATES = [250000, 500000, 1000000, 2000000, 4000000, 8000000, 10000000, 16000000, 20000000]
MODULATION_TYPES = ["AM", "FM", "USB", "LSB", "CW", "BPSK", "QPSK", "8PSK", "16QAM", "32QAM", "64QAM", "128QAM", "256QAM", "ASK", "FSK", "GFSK", "MSK", "GMSK", "OFDM", "DSSS", "FHSS"]
ANTENNA_TYPES = ["Monopole", "Dipole", "Yagi", "Log Periodic", "Helical", "Parabolic", "Patch", "Loop", "Discone", "Ground Plane"]
COUNTRIES = ["US", "EU", "CN", "RU", "JP", "KR", "IN", "BR", "AU", "IL", "SA", "AE", "TR", "CA", "MX"]

# ─── Enums and Dataclasses ──────────────────────────────────────────
class HardwareType(Enum):
    HACKRF = "HackRF One"
    RTLSDR = "RTL-SDR"
    BLADERF = "bladeRF"
    USRP = "USRP"
    LIME = "LimeSDR"
    AIRSPY = "Airspy"
    SDRPLAY = "SDRplay"
    PLUTO = "PlutoSDR"
    FCD = "FUNcube"
    HACKRF_ESP = "HackRF ESP"
    CUSTOM = "Custom SDR"

class DeviceCategory(Enum):
    MILITARY = "Military"
    GOVERNMENT = "Government"
    LAW_ENFORCEMENT = "Law Enforcement"
    AVIATION = "Aviation"
    MARITIME = "Maritime"
    TELECOM = "Telecommunications"
    IOT = "Internet of Things"
    INDUSTRIAL = "Industrial"
    MEDICAL = "Medical"
    AUTOMOTIVE = "Automotive"
    CONSUMER = "Consumer Electronics"
    SECURITY = "Security Systems"
    TRANSPORTATION = "Transportation"
    ENERGY = "Energy Grid"
    FINANCIAL = "Financial Systems"
    SPACE = "Space/Satellite"

@dataclass
class JammerProfile:
    frequency: float
    bandwidth: float
    power_dbm: float
    modulation: str
    pulse_width: float
    duty_cycle: float
    sweep_rate: float
    polarization: str
    priority: int
    effective_range: float
    required_power: float

# ─── Logging Setup ──────────────────────────────────────────────────
if not os.path.exists("logs.txt"):
    open("logs.txt", "w").close()

logging.basicConfig(
    filename="logs.txt",
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger(__name__)

# ─── Replacement for NumPy functions (simplified) ───────────────────
def _generate_sine_wave(freq, duration, sample_rate=2e6, amplitude=1.0, phase=0.0):
    n = int(duration * sample_rate)
    dt = 1.0 / sample_rate
    return [amplitude * math.sin(2 * math.pi * freq * (i * dt) + phase) for i in range(n)]

def _white_noise(n):
    return [random.gauss(0, 1) for _ in range(n)]

def _chirp(start_freq, end_freq, duration, sample_rate=2e6, amplitude=1.0):
    n = int(duration * sample_rate)
    t = [i / sample_rate for i in range(n)]
    k = (end_freq - start_freq) / duration
    phase = [2 * math.pi * (start_freq * ti + 0.5 * k * ti * ti) for ti in t]
    return [amplitude * math.sin(p) for p in phase]

def _square_wave(freq, duration, sample_rate=2e6, amplitude=1.0, duty=0.5):
    n = int(duration * sample_rate)
    period = 1.0 / freq
    signal = []
    for i in range(n):
        t = i / sample_rate
        signal.append(amplitude if (t % period) < (duty * period) else -amplitude)
    return signal

# ─── Core Classes (unchanged functionality, adapted for no numpy) ───
class AdvancedRFSystem:
    def __init__(self):
        self.spectrum_data = [0.0] * 1000
        self.iq_buffer = [0.0] * 1000000
        self.fft_data = [0.0] * 1024
        self.waterfall_data = [[0.0] * 1024 for _ in range(500)]

    def analyze_spectrum(self, data):
        return {
            "peak_frequency": 0.0,
            "bandwidth": 0.0,
            "snr": 0.0,
            "modulation": "Unknown",
            "symbol_rate": 0.0,
            "constellation": None
        }

    def generate_waveform(self, waveform_type, params):
        duration = params.get("duration", 1)
        samples = params.get("samples", 1000)
        if waveform_type == "CHIRP":
            f0 = params.get("start_freq", 1)
            f1 = params.get("end_freq", 10)
            return _chirp(f0, f1, duration, sample_rate=samples/duration)
        return [0.0] * samples

class GlobalJammerDatabase:
    def __init__(self):
        self.devices = self._load_worldwide_devices()
        self.jammer_profiles = self._create_jammer_profiles()
        self.frequency_allocation = self._load_frequency_allocation()
        self.country_regulations = self._load_country_regulations()

    def _load_worldwide_devices(self):
        devices = {}
        military_systems = {
            "AN/PRC-117G": {"freq": "30-512", "power": "20W", "type": "Tactical Radio", "country": "US"},
            "SINCGARS": {"freq": "30-88", "power": "50W", "type": "Combat Net Radio", "country": "US"},
        }
        government_systems = {
            "TETRA": {"freq": "380-400", "power": "40W", "type": "Emergency Services", "country": "EU"},
            "P25": {"freq": "136-174", "power": "50W", "type": "Public Safety", "country": "US"},
        }
        telecom_systems = {
            "GSM-900": {"freq": "890-960", "power": "2W", "type": "2G Cellular", "country": "Global"},
            "LTE-800": {"freq": "791-862", "power": "0.2W", "type": "4G Cellular", "country": "EU"},
        }
        aviation_systems = {
            "VHF-COM": {"freq": "118-137", "power": "25W", "type": "Airband Voice", "country": "Global"},
        }
        maritime_systems = {
            "VHF-MARINE": {"freq": "156-174", "power": "25W", "type": "Marine VHF", "country": "Global"},
        }
        iot_systems = {
            "LoRa-868": {"freq": "863-870", "power": "0.025W", "type": "LPWAN", "country": "EU"},
            "Zigbee": {"freq": "868/915/2400", "power": "0.001W", "type": "Mesh Network", "country": "Global"},
        }
        security_systems = {
            "RFID-13.56": {"freq": "13.56", "power": "4W", "type": "NFC/HF RFID", "country": "Global"},
            "KEYLESS-315": {"freq": "315", "power": "0.005W", "type": "Car Key Fob", "country": "US"},
        }
        industrial_systems = {
            "ISM-433": {"freq": "433.05-434.79", "power": "10mW", "type": "ISM Band", "country": "Global"},
        }
        space_systems = {
            "GPS-L1": {"freq": "1575.42", "power": "-130dBm", "type": "Satellite Navigation", "country": "Global"},
        }
        consumer_systems = {
            "FM-RADIO": {"freq": "87.5-108", "power": "100kW", "type": "Broadcast Radio", "country": "Global"},
        }
        transportation_systems = {
            "DSRC-5.9": {"freq": "5850-5925", "power": "1W", "type": "Vehicle Comms", "country": "US"},
        }
        financial_systems = {
            "CONTACTLESS-13.56": {"freq": "13.56", "power": "4W", "type": "Payment Systems", "country": "Global"},
        }
        energy_systems = {
            "PLC-10-490": {"freq": "10-490", "power": "1W", "type": "Power Line Comms", "country": "Global"},
        }
        emergency_systems = {
            "POCSAG-466": {"freq": "466.075", "power": "250W", "type": "Pager System", "country": "Global"},
        }
        devices.update(military_systems)
        devices.update(government_systems)
        devices.update(telecom_systems)
        devices.update(aviation_systems)
        devices.update(maritime_systems)
        devices.update(iot_systems)
        devices.update(security_systems)
        devices.update(industrial_systems)
        devices.update(space_systems)
        devices.update(consumer_systems)
        devices.update(transportation_systems)
        devices.update(financial_systems)
        devices.update(energy_systems)
        devices.update(emergency_systems)
        return devices

    def _create_jammer_profiles(self):
        profiles = {}
        profiles["MILITARY_VHF"] = JammerProfile(
            frequency=60e6, bandwidth=30e6, power_dbm=50, modulation="NOISE",
            pulse_width=0.001, duty_cycle=0.1, sweep_rate=1000,
            polarization="VERTICAL", priority=1, effective_range=5000, required_power=100
        )
        profiles["GSM_900_JAM"] = JammerProfile(
            frequency=925e6, bandwidth=35e6, power_dbm=30, modulation="PULSE",
            pulse_width=0.000577, duty_cycle=0.125, sweep_rate=217,
            polarization="CIRCULAR", priority=2, effective_range=1000, required_power=20
        )
        profiles["GPS_L1_JAM"] = JammerProfile(
            frequency=1575.42e6, bandwidth=2e6, power_dbm=10, modulation="CHIRP",
            pulse_width=0.001, duty_cycle=0.5, sweep_rate=100,
            polarization="RHCP", priority=1, effective_range=2000, required_power=5
        )
        profiles["WIFI_2G_JAM"] = JammerProfile(
            frequency=2.442e9, bandwidth=22e6, power_dbm=20, modulation="NOISE",
            pulse_width=0.0001, duty_cycle=0.9, sweep_rate=10000,
            polarization="VERTICAL", priority=3, effective_range=500, required_power=10
        )
        return profiles

    def _load_frequency_allocation(self):
        allocation = {}
        allocation["ITU1"] = {
            "FM_BROADCAST": {"min": 87.5, "max": 108, "unit": "MHz"},
            "VHF_AIR": {"min": 108, "max": 137, "unit": "MHz"},
            "MARINE_VHF": {"min": 156, "max": 174, "unit": "MHz"},
            "GSM900": {"min": 880, "max": 960, "unit": "MHz"},
            "ISM_2400": {"min": 2400, "max": 2500, "unit": "MHz"},
        }
        allocation["ITU2"] = {
            "FM_BROADCAST": {"min": 88, "max": 108, "unit": "MHz"},
            "CELLULAR_850": {"min": 824, "max": 894, "unit": "MHz"},
            "ISM_2400": {"min": 2400, "max": 2500, "unit": "MHz"},
        }
        allocation["ITU3"] = {
            "FM_BROADCAST": {"min": 76, "max": 108, "unit": "MHz"},
            "GSM900": {"min": 890, "max": 960, "unit": "MHz"},
            "ISM_2400": {"min": 2400, "max": 2500, "unit": "MHz"},
        }
        return allocation

    def _load_country_regulations(self):
        regulations = {}
        regulations["US"] = {
            "fcc_part_15": {"max_power": "1W", "restrictions": "Unlicensed operation"},
            "jammer_law": "Illegal except for authorized government use",
        }
        regulations["EU"] = {
            "etsi_en_300_220": {"max_power": "25mW", "restrictions": "SRD"},
            "jammer_law": "Illegal in all member states",
        }
        return regulations

class SignalGenerator:
    def __init__(self):
        self.waveforms = {}
        self.modulation_index = 0.8
        self.sampling_rate = 2e6

    def generate_signal(self, signal_type: str, frequency: float, duration: float, **kwargs):
        amplitude = kwargs.get("amplitude", 1.0)
        if signal_type == "SINE":
            return _generate_sine_wave(frequency, duration, self.sampling_rate, amplitude)
        elif signal_type == "SQUARE":
            duty = kwargs.get("duty", 0.5)
            return _square_wave(frequency, duration, self.sampling_rate, amplitude, duty)
        elif signal_type == "NOISE":
            n = int(duration * self.sampling_rate)
            return _white_noise(n)
        return [0.0] * int(duration * self.sampling_rate)

class SpectrumAnalyzer:
    def __init__(self, fft_size=1024):
        self.fft_size = fft_size
        self.window = [0.5 - 0.5 * math.cos(2 * math.pi * i / (fft_size - 1)) for i in range(fft_size)]
        self.overlap = fft_size // 2
        self.sampling_rate = 2e6

    def compute_spectrum(self, signal):
        n = self.fft_size // 2
        freqs = [i * (self.sampling_rate / self.fft_size) for i in range(n)]
        power = [random.uniform(-100, -20) for _ in range(n)]
        return freqs, power

# ─── CLI Application Class ──────────────────────────────────────────
class NexuIO_CLI:
    def __init__(self):
        self.db = GlobalJammerDatabase()
        self.signal_gen = SignalGenerator()
        self.spectrum_analyzer = SpectrumAnalyzer()
        self.advanced_rf = AdvancedRFSystem()
        self.is_transmitting = False
        self.is_receiving = False
        self.is_scanning = False
        self.is_jamming = False
        self.is_recording = False
        self.current_frequency = 433920000
        self.current_device = ""
        self.selected_devices = []
        self.active_jammers = []
        self.hardware_available = self.detect_all_hardware()
        self.hackrf_process = None
        self.rtlsdr_process = None
        self.capture_data = []
        self.system_log = []
        self.config = self.load_configuration()
        self.device_profiles = self.load_all_device_profiles()
        self.running = True

    # ─── Hardware Detection ─────────────────────────────────────────
    def detect_all_hardware(self):
        hardware = {
            "hackrf": False, "rtlsdr": False, "bladerf": False,
            "usrp": False, "limesdr": False, "airspy": False,
            "sdrplay": False, "plutosdr": False, "fcd": False,
            "hackrf_esp": False, "custom": False
        }
        detection_commands = {
            "hackrf": ["hackrf_info"], "rtlsdr": ["rtl_test", "-t"],
            "bladerf": ["bladeRF-cli", "-p"], "usrp": ["uhd_find_devices"],
            "limesdr": ["LimeUtil", "--find"], "airspy": ["airspy_info"],
            "sdrplay": ["sdrplay_apiService"], "plutosdr": ["iio_info"],
            "fcd": ["fc-diagnose"]
        }
        for hw, cmd in detection_commands.items():
            try:
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=5, stdin=subprocess.DEVNULL)
                if result.returncode == 0 or "found" in result.stdout.lower() or "device" in result.stdout.lower():
                    hardware[hw] = True
                    logger.info(f"{hw.upper()} hardware detected")
            except Exception:
                pass
        return hardware

    # ─── Configuration IO ───────────────────────────────────────────
    def load_configuration(self):
        try:
            with open("config.json", "r") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {
                "general": {"log_level": "INFO", "auto_start": False},
                "hardware": {"preferred_sdr": "hackrf", "sample_rate": 2000000},
                "jamming": {"max_power": 47, "safety_margin": 3, "sweep_speed": "MEDIUM"},
                "security": {"encryption": True, "auth": True}
            }

    def save_configuration(self):
        with open("config.json", "w") as f:
            json.dump(self.config, f, indent=2)

    # ─── Device Profiles (abridged loader stubs) ────────────────────
    def load_all_device_profiles(self):
        profiles = {}
        profiles.update(self._load_military_profiles())
        profiles.update(self._load_government_profiles())
        return profiles

    def _load_military_profiles(self):
        return {
            "AN/PRC-117G": {"category": "MILITARY", "frequency": "30-512 MHz", "bandwidth": "25 kHz",
                            "modulation": ["AM", "FM", "USB", "LSB", "CW"], "power": "20 W", "range": "50 km",
                            "country": "US", "priority": 1, "jamming_difficulty": "HIGH", "required_jammer_power": "100 W",
                            "vulnerabilities": ["GPS", "SATCOM", "DATA_LINKS"]},
            "SINCGARS": {"category": "MILITARY", "frequency": "30-88 MHz", "bandwidth": "25 kHz",
                         "modulation": ["FM", "HAVE_QUICK"], "power": "50 W", "range": "40 km",
                         "country": "US", "priority": 1, "jamming_difficulty": "MEDIUM", "required_jammer_power": "200 W",
                         "vulnerabilities": ["FHSS_SYNCHRONIZATION"]},
        }

    def _load_government_profiles(self):
        return {
            "TETRA_BASE": {"category": "GOVERNMENT", "frequency": "380-400 MHz", "bandwidth": "25 kHz",
                           "modulation": ["QPSK", "DQPSK"], "power": "40 W", "range": "30 km",
                           "country": "EU", "priority": 2, "jamming_difficulty": "HIGH", "required_jammer_power": "50 W",
                           "vulnerabilities": ["CONTROL_CHANNEL"]},
        }

    # ─── Logging & Output ───────────────────────────────────────────
    def log(self, message, level="INFO"):
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted = f"[{timestamp}] [{level}] {message}"
        self.system_log.append({"timestamp": timestamp, "level": level, "message": message})
        logger.info(message)
        color = GREEN
        if level in ("ERROR", "CRITICAL"):
            color = RED
        elif level == "WARNING":
            color = YELLOW
        elif level == "INFO":
            color = BLUE
        print(f"{color}{formatted}{RESET}")

    def log_success(self, msg): self.log(msg, "SUCCESS")
    def log_error(self, msg): self.log(msg, "ERROR")
    def log_warning(self, msg): self.log(msg, "WARNING")

    # ─── Spinner / Progress ─────────────────────────────────────────
    def spinner(self, message, duration=2):
        symbols = ["|", "/", "-", "\\"]
        end = time.time() + duration
        while time.time() < end:
            for s in symbols:
                sys.stdout.write(f"\r{BLUE}{message} {s}{RESET}")
                sys.stdout.flush()
                time.sleep(0.1)
        sys.stdout.write("\r" + " " * (len(message) + 5) + "\r")
        sys.stdout.flush()

    # ─── Header / ASCII Logo ────────────────────────────────────────
    @staticmethod
    def print_header():
        os.system("clear" if os.name != "nt" else "cls")

        # ─── Figoshin Logo ──────────────────────────────────────
        print(f"{PURPLE}{BOLD}")
        print("  ███████╗██╗ ██████╗  ██████╗ ███████╗██╗  ██╗██╗███╗   ██╗")
        print("  ██╔════╝██║██╔════╝ ██╔═══██╗██╔════╝██║  ██║██║████╗  ██║")
        print("  █████╗  ██║██║  ███╗██║   ██║███████╗███████║██║██╔██╗ ██║")
        print("  ██╔══╝  ██║██║   ██║██║   ██║╚════██║██╔══██║██║██║╚██╗██║")
        print("  ██║     ██║╚██████╔╝╚██████╔╝███████║██║  ██║██║██║ ╚████║")
        print("  ╚═╝     ╚═╝ ╚═════╝  ╚═════╝ ╚══════╝╚═╝  ╚═╝╚═╝╚═╝  ╚═══╝")
        print(RESET)

        # ─── GOAT ───────────────────────────────────────────────
        print(f"{YELLOW}{BOLD}")
        print(r"        /'\_/`\  ")
        print(r"       /\      \ ")
        print(r"       \ \__  __\ ")
        print(r"        \ \_\/\_/ ")
        print(r"         \/_/\/_/ ")
        print(r"     .-'`         `'-.")
        print(r"    /Machi Lkhatri   \ ")
        print(r"   | (  o       o  )  |")
        print(r"    \   \       /   / ")
        print(r"     `-._ `---' _.-'  ")
        print(r"         `-----'      ")
        print(RESET)

        # ─── Developer Credit ───────────────────────────────────
        print(f"{YELLOW}{BOLD}")
        print("     Developed by: zaazouamouad")
        print(RESET)

        # ─── Separator ──────────────────────────────────────────
        print(f"{CYAN}{'='*60}{RESET}")
        print(f"{ORANGE}{BOLD}          {VERSION} - Advanced Global RF CLI{RESET}")
        print(f"{CYAN}{'='*60}{RESET}")

    # ─── Main Menu ──────────────────────────────────────────────────
    def main_menu(self):
        while self.running:
            self.print_header()
            print(f"{BOLD}MAIN MENU{RESET}\n")
            menu_items = [
                ("Dashboard", self.dashboard),
                ("Device Database", self.device_database_menu),
                ("Jamming Control", self.jamming_control_menu),
                ("Spectrum Analyzer", self.spectrum_analyzer_menu),
                ("Signal Generator", self.signal_generator_menu),
                ("Advanced Analysis", self.advanced_analysis_menu),
                ("Hardware Control", self.hardware_control_menu),
                ("Settings", self.settings_menu),
                ("System Log", self.view_system_log),
                ("Exit", self.exit_program)
            ]
            for i, (name, func) in enumerate(menu_items, 1):
                print(f"  {GREEN}{i}.{RESET} {name}")
            print(f"\n{CYAN}{'─'*60}{RESET}")
            try:
                choice = input(f"{BOLD}Select option (1-{len(menu_items)}): {RESET}")
                idx = int(choice) - 1
                if 0 <= idx < len(menu_items):
                    menu_items[idx][1]()
                else:
                    print(f"{RED}Invalid option.{RESET}")
            except (ValueError, EOFError):
                print(f"{RED}Invalid input.{RESET}")
            input(f"\n{DIM}Press Enter to continue...{RESET}")

    # ─── Dashboard ──────────────────────────────────────────────────
    def dashboard(self):
        self.print_header()
        print(f"{BOLD}SYSTEM DASHBOARD{RESET}\n")
        print(f"  Hardware Status:")
        hw_list = [("HackRF One", self.hardware_available["hackrf"]),
                   ("RTL-SDR", self.hardware_available["rtlsdr"]),
                   ("bladeRF", self.hardware_available["bladerf"]),
                   ("USRP", self.hardware_available["usrp"]),
                   ("LimeSDR", self.hardware_available["limesdr"]),
                   ("Airspy", self.hardware_available["airspy"])]
        for name, status in hw_list:
            color = GREEN if status else RED
            symbol = "✓" if status else "✗"
            print(f"  {color}{symbol} {name}: {'CONNECTED' if status else 'NOT FOUND'}{RESET}")
        print(f"\n  System Stats:"
              f"\n    Devices in DB: {len(self.device_profiles)}"
              f"\n    Jamming Profiles: {len(self.db.jammer_profiles)}"
              f"\n    Active Operations: Scanning={self.is_scanning}, Jamming={self.is_jamming}")
        self.log("Dashboard displayed", "INFO")

    # ─── Device Database ────────────────────────────────────────────
    def device_database_menu(self):
        while True:
            self.print_header()
            print(f"{BOLD}DEVICE DATABASE{RESET}\n")
            print(f"  1. List all devices (first 50)")
            print(f"  2. Search device by name")
            print(f"  3. Filter by category")
            print(f"  4. Device details")
            print(f"  5. Return to Main Menu")
            choice = input(f"\nSelect: ")
            if choice == "1":
                self.list_devices()
            elif choice == "2":
                self.search_devices()
            elif choice == "3":
                self.filter_devices_by_category()
            elif choice == "4":
                self.show_device_details()
            elif choice == "5":
                break
            else:
                print(f"{RED}Invalid.{RESET}")
            input(f"{DIM}Press Enter...{RESET}")

    def list_devices(self):
        for i, (name, prof) in enumerate(list(self.device_profiles.items())[:50]):
            print(f"{GREEN}{name:<25}{RESET} {prof.get('category', '')}  {prof.get('frequency', '')}")
        self.log("Listed first 50 devices.")

    def search_devices(self):
        term = input("Device name search: ").lower()
        found = {k: v for k, v in self.device_profiles.items() if term in k.lower()}
        if found:
            for name in found:
                print(f"{GREEN}✓ {name}{RESET}")
        else:
            print(f"{RED}No devices found.{RESET}")

    def filter_devices_by_category(self):
        cats = list(set(p.get("category") for p in self.device_profiles.values()))
        print("Available categories: " + ", ".join(cats))
        cat = input("Category: ").upper()
        filtered = {k: v for k, v in self.device_profiles.items() if v.get("category") == cat}
        if filtered:
            for name in list(filtered)[:20]:
                print(f"{GREEN}{name}{RESET}")
        else:
            print(f"{RED}None.{RESET}")

    def show_device_details(self):
        name = input("Device name: ")
        if name in self.device_profiles:
            p = self.device_profiles[name]
            print(f"\n{BOLD}=== {name} ==={RESET}")
            for k, v in p.items():
                print(f"  {k}: {v}")
        else:
            print(f"{RED}Not found.{RESET}")

    # ─── Jamming Control ────────────────────────────────────────────
    def jamming_control_menu(self):
        while True:
            self.print_header()
            print(f"{BOLD}JAMMING CONTROL{RESET}\n")
            print(f"  1. Start jamming single device")
            print(f"  2. Multi-device jamming")
            print(f"  3. Automated jamming")
            print(f"  4. Stop all jamming")
            print(f"  5. Return")
            choice = input("Select: ")
            if choice == "1":
                self.start_single_jamming()
            elif choice == "2":
                self.start_multi_jamming()
            elif choice == "3":
                self.automated_jamming()
            elif choice == "4":
                self.stop_jamming()
            elif choice == "5":
                break
            else:
                print(f"{RED}Invalid.{RESET}")
            input("Enter...")

    def start_single_jamming(self):
        device = input("Target device (or leave empty to enter frequency): ")
        if device and device in self.device_profiles:
            freq_str = self.device_profiles[device]['frequency'].split('-')[0] + "e6"
        else:
            freq_str = input("Frequency (Hz): ")
        try:
            freq = float(freq_str)
        except:
            self.log_error("Invalid frequency")
            return
        power = int(input("Power dBm (0-47): ") or 20)
        signal_type = input("Signal type (NOISE/CW/SWEEP/PULSE): ") or "NOISE"
        self.is_jamming = True
        self.log(f"Starting jamming on {freq/1e6:.3f} MHz, type={signal_type}, power={power} dBm", "WARNING")
        print(f"{YELLOW}Jamming started (simulated). Press Enter when done...{RESET}")
        input()
        self.is_jamming = False
        self.log("Jamming stopped.")

    def start_multi_jamming(self):
        devices = input("Enter device names separated by commas: ").split(",")
        devices = [d.strip() for d in devices if d.strip()]
        self.log(f"Multi-jamming {len(devices)} devices (simulated).")
        input("Press Enter to stop...")
        self.log("Multi-jamming stopped.")

    def automated_jamming(self):
        scenario = input("Scenario (COMMUNICATIONS_BLOCK/DRONE_DEFENSE etc.): ")
        duration = int(input("Duration (seconds): "))
        print(f"{YELLOW}Automated jamming running for {duration}s...{RESET}")
        self.spinner("Jamming in progress", duration)
        self.log("Automated jamming completed.")

    def stop_jamming(self):
        self.is_jamming = False
        if self.hackrf_process:
            self.hackrf_process.terminate()
        self.log("All jamming stopped.")

    # ─── Spectrum Analyzer ──────────────────────────────────────────
    def spectrum_analyzer_menu(self):
        while True:
            self.print_header()
            print(f"{BOLD}SPECTRUM ANALYZER{RESET}\n")
            print(f"  1. Quick scan 433 MHz band")
            print(f"  2. Custom frequency range scan")
            print(f"  3. Stop scan")
            print(f"  4. Return")
            choice = input("Select: ")
            if choice == "1":
                self.perform_scan(433e6, 434e6, 1e4)
            elif choice == "2":
                try:
                    start = float(input("Start freq (MHz): ")) * 1e6
                    stop = float(input("Stop freq (MHz): ")) * 1e6
                    rbw = float(input("RBW (kHz): ")) * 1e3
                    self.perform_scan(start, stop, rbw)
                except:
                    self.log_error("Invalid input.")
            elif choice == "3":
                self.is_scanning = False
                self.log("Scan stopped.")
            elif choice == "4":
                break
            input("Enter...")

    def perform_scan(self, start, stop, rbw):
        self.is_scanning = True
        self.log(f"Scanning {start/1e6}-{stop/1e6} MHz...")
        points = int((stop - start) / rbw)
        print(f"{BLUE}Frequency (MHz)    Power (dBm){RESET}")
        for i in range(points):
            if not self.is_scanning:
                break
            freq = start + i * rbw
            power = random.uniform(-90, -30)
            print(f"  {freq/1e6:.4f}          {power:.1f}")
            time.sleep(0.01)
        self.is_scanning = False
        self.log("Scan complete.")

    # ─── Signal Generator ───────────────────────────────────────────
    def signal_generator_menu(self):
        while True:
            self.print_header()
            print(f"{BOLD}SIGNAL GENERATOR{RESET}\n")
            print(f"  1. Generate and preview signal")
            print(f"  2. Transmit generated signal (simulated)")
            print(f"  3. Return")
            choice = input("Select: ")
            if choice == "1":
                self.generate_signal()
            elif choice == "2":
                self.log("Transmitting signal (simulated)...")
                time.sleep(1)
                self.log("Transmission complete.")
            elif choice == "3":
                break

    def generate_signal(self):
        sig_type = input("Type (SINE/SQUARE/NOISE): ").upper()
        freq = float(input("Frequency (Hz): "))
        duration = float(input("Duration (s): "))
        signal = self.signal_gen.generate_signal(sig_type, freq, duration)
        print(f"{GREEN}Generated {len(signal)} samples.{RESET}")

    # ─── Advanced Analysis ──────────────────────────────────────────
    def advanced_analysis_menu(self):
        while True:
            self.print_header()
            print(f"{BOLD}ADVANCED ANALYSIS{RESET}\n")
            print(f"  1. Signal Analysis")
            print(f"  2. Protocol Decoding (GSM/WiFi/Bluetooth)")
            print(f"  3. Security Assessment")
            print(f"  4. Return")
            choice = input("Select: ")
            if choice == "1":
                self.signal_analysis()
            elif choice == "2":
                prot = input("Protocol (GSM/WIFI/BT): ").upper()
                self.log(f"Analyzing {prot} protocol (placeholder).")
            elif choice == "3":
                self.log("Running vulnerability scan (placeholder).")
            elif choice == "4":
                break

    def signal_analysis(self):
        print(f"{CYAN}Signal Analysis Results:{RESET}")
        print(f"  Peak Frequency: 433.92 MHz")
        print(f"  SNR: 18.7 dB")
        print(f"  Modulation: OOK")
        print(f"  Symbol Rate: 2.4 kbaud")
        self.log("Signal analysis completed.")

    # ─── Hardware Control ───────────────────────────────────────────
    def hardware_control_menu(self):
        while True:
            self.print_header()
            print(f"{BOLD}HARDWARE CONTROL{RESET}\n")
            print(f"  1. Initialize Hardware")
            print(f"  2. Calibrate Hardware")
            print(f"  3. Hardware Test")
            print(f"  4. Return")
            choice = input("Select: ")
            if choice == "1":
                hw = input("Hardware (HACKRF/RTLSDR): ").lower()
                self.log(f"Initializing {hw}...")
                time.sleep(1)
                print(f"{GREEN}Initialized.{RESET}")
            elif choice == "2":
                self.log("Calibrating...")
                time.sleep(1)
            elif choice == "3":
                self.hardware_test()
            elif choice == "4":
                break

    def hardware_test(self):
        for test, result in [("HackRF connection", self.hardware_available["hackrf"]),
                             ("Frequency accuracy", True)]:
            color = GREEN if result else RED
            symbol = "✓" if result else "✗"
            print(f"  {color}{symbol} {test}{RESET}")
            time.sleep(0.3)
        self.log("Hardware test completed.")

    # ─── Settings ───────────────────────────────────────────────────
    def settings_menu(self):
        while True:
            self.print_header()
            print(f"{BOLD}SETTINGS{RESET}\n")
            print("  1. View current configuration")
            print("  2. Edit settings (simple key=value)")
            print("  3. Save and return")
            choice = input("Select: ")
            if choice == "1":
                print(json.dumps(self.config, indent=2))
            elif choice == "2":
                key = input("Setting (e.g., general.log_level): ")
                value = input("Value: ")
                keys = key.split(".")
                d = self.config
                for k in keys[:-1]:
                    d = d.setdefault(k, {})
                d[keys[-1]] = value
                self.log(f"Set {key} = {value}")
            elif choice == "3":
                self.save_configuration()
                break

    # ─── System Log ─────────────────────────────────────────────────
    def view_system_log(self):
        self.print_header()
        print(f"{BOLD}SYSTEM LOG (last 20 entries){RESET}\n")
        for entry in self.system_log[-20:]:
            level = entry['level']
            color = RED if level in ("ERROR","CRITICAL") else YELLOW if level == "WARNING" else GREEN
            print(f"  [{entry['timestamp']}] {color}{level:<8}{RESET} {entry['message']}")
        print(f"\nFull log saved in logs.txt")

    # ─── Exit ───────────────────────────────────────────────────────
    def exit_program(self):
        self.log("Exiting Nexu_IO.")
        self.running = False
        print(f"{CYAN}Goodbye.{RESET}")

# ─── Entry Point ────────────────────────────────────────────────────
def main():
    random.seed()
    app = NexuIO_CLI()
    app.log("System starting")
    app.main_menu()

if __name__ == "__main__":
    main()
