"""Constants for the Kef Connector integration."""

from datetime import timedelta

DOMAIN = "kef_connector"

CONF_MAX_VOLUME = "maximum_volume"
CONF_VOLUME_STEP = "volume_step"
CONF_SPEAKER_MODEL = "speaker_model"

DEFAULT_NAME = "DEFAULT_KEFSPEAKER"
DEFAULT_MAX_VOLUME = 1.0
DEFAULT_VOLUME_STEP = 0.03
DEFAULT_SPEAKER_MODEL = "default"

SCAN_INTERVAL = timedelta(seconds=10)

UNIQUE_ID_PREFIX = "KEF_SPEAKER"

SOURCES = {
    "LSX2": ["wifi", "bluetooth", "tv", "optical", "analog", "usb"],
    "LSX2LT": ["wifi", "bluetooth", "tv", "optical", "usb"],
    "LS50W2": ["wifi", "bluetooth", "tv", "optical", "coaxial", "analog"],
    "LS60": ["wifi", "bluetooth", "tv", "optical", "coaxial", "analog"],
    "XIO": ["wifi", "bluetooth", "tv", "optical"],
    "default": ["wifi", "bluetooth", "tv", "optical", "coaxial", "analog", "usb"],
}

# Human readable labels for the model selector in the UI
MODEL_LABELS = {
    "LSX2": "LSX II",
    "LSX2LT": "LSX II LT",
    "LS50W2": "LS50 Wireless II",
    "LS60": "LS60 Wireless",
    "XIO": "XIO Soundbar",
    "default": "Other / unknown (all sources)",
}

# Model names as reported by the speaker firmware -> keys of SOURCES
FIRMWARE_MODELS = {
    "LSXII": "LSX2",
    "LSXIILT": "LSX2LT",
    "LS50WII": "LS50W2",
    "LS60": "LS60",
    "XIO": "XIO",
}
