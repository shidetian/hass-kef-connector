# 🏠️↔️🔉 Kef Connector
A Home Assistant integration for KEF speakers 🔊

Kef Connector is compatible with LSX2LT, LSX2, LS50W2, LS60 and XIO Soundbar.

- [🏠️↔️🔉 Kef Connector](#️️-kef-connector)
  - [Installation and configuration](#installation-and-configuration)
    - [⬇️ Installation](#️-installation)
    - [🔧 Configuration](#-configuration)
      - [📜 Options](#-options)
      - [🔁 Migrating from `configuration.yaml`](#-migrating-from-configurationyaml)


## Installation and configuration

### ⬇️ Installation
This custom component is available on [HACS](https://hacs.xyz) !\
You can also install it manually, but HACS is the recommended method (see bellow for "manual installation").
Simply search for Kef Connector on HACS and clic download. Do not forget to restart home assistant and then follow the instructions in the [configuration](#-configuration) section.

**Manual Installation**\
Copy the [kef_connector](custom_components/kef_connector) folder in your home assistant `config/custom_components` folder, and then follow the [configuration](#-configuration) section.

### 🔧 Configuration

Kef Connector is configured from the Home Assistant UI:

1. Go to **Settings → Devices & services** and click **Add integration**.
2. Search for **Kef Connector**.
3. Enter the IP address of your speakers. More information on how to find it [here](https://github.com/N0ciple/pykefcontrol#-get-the-ip-address).
4. Kef Connector connects to the speakers, detects their name and model, and lets you confirm the model and volume settings.

Repeat for each pair of speakers. If the IP address of your speakers changes, use **Reconfigure** on the integration entry.

#### 📜 Options

These can be changed at any time with **Configure** on the integration entry.

| option           | default value | comment|
| ---------------- | ------------- | -------------------- |
| Speaker model    | _auto-detected_ | Model of your KEF speakers (`LSX II`, `LSX II LT`, `LS50 Wireless II`, `LS60` or `XIO`). This lets Kef Connector know which sources are available on your speakers. If set to "Other / unknown", all sources will be available on the entity, even though they are not physically present on your speakers (for example, there is no analog input on the LSX2LT). |
| Maximum volume   | `1.0`         | A number between 0 and 1. 0 is muted and 1 is maximum volume. Bear in mind that this option **does not** override the maximum volume set in the KefConnect app. It will prevent hass from setting a volume higher than the maximum volume. |
| Volume step      | `0.03`        | A number between 0 and 1 (however it is **not recommended** to set it higher than 0.1). This value is by how much volume will be changed when calling `media_player.volume_up` or `media_player.volume_down` services, by clicking on ![volume_down_up](assets/images/volume_down_up.png) for example. |

The name of the speakers is taken from the KefConnect app. You can rename the entity or the integration entry from the UI.

#### 🔁 Migrating from `configuration.yaml`

Older versions of Kef Connector were configured in `configuration.yaml`. Existing `kef_connector` entries are automatically imported into the UI on startup (the speakers must be reachable), keeping your entity IDs and settings. Once imported, a repair notice will ask you to remove the `kef_connector` entries from `configuration.yaml` and restart Home Assistant.
